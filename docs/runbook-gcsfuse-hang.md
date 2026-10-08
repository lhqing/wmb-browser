# Runbook: site hangs (504) because a gcsfuse mount froze

On 2026-10-08 we restored <https://mousebrain.salk.edu> after it had been down since about 2026-08-06. The gcsfuse mount at `/browser` had stopped answering while its process stayed alive. That froze every gunicorn worker and part of the HiGlass server. We fixed it by aborting the dead FUSE connection, remounting the bucket and restarting the app processes. The VM was not rebooted.

## Timeline (UTC)

| When | What |
| --- | --- |
| 2026-07-14 (approx.) | `dmesg` first reports gunicorn workers "blocked for more than 120 seconds" in FUSE calls. The time is approximate because `dmesg -T` drifts after long uptimes. |
| 2026-08-06 15:31 | Last request served (`~/access.log`). |
| 2026-08-06 15:33 | `[CRITICAL] WORKER TIMEOUT` is the last line in `~/error.log`. The site is down from here on. |
| 2026-10-08 04:44 | Gunicorn master stopped, and the `/browser` FUSE connection aborted. |
| 2026-10-08 04:48 | `/browser` remounted, HiGlass restarted and gunicorn relaunched. The site is back. |

## Symptoms

- `http://mousebrain.salk.edu` returns its 301, so nginx is up. `https://` connects (TLS is fine) but hangs, then returns **504** after 60 s.
- The nginx error log shows `upstream timed out (110: Connection timed out) while connecting to upstream ... "http://127.0.0.1:8000/"`.
- The HiGlass API at `https://mousebrain.salk.edu:8001/api/v1/tilesets/` hangs too.
- The load average holds flat at the number of stuck processes (5.0 on 4 vCPUs) while CPU use stays low.
- Gunicorn's `~/error.log` ends at a `WORKER TIMEOUT` with nothing after it.

## Why it happens

- **gcsfuse stops answering.** The gcsfuse 1.3.0 process serving `/browser` stays alive but stops replying to the kernel. Any process that touches `/browser` then blocks in uninterruptible sleep (state `D`). In `/proc/<pid>/stack` that looks like `request_wait_answer` → `fuse_simple_request` → `fuse_do_getattr`.
- **Gunicorn can't recover.** Its master SIGKILLs timed-out workers, but a process in `D` state ignores even SIGKILL. The workers never exit, the master never replaces them, and nginx times out.
- **HiGlass is caught too.** The HiGlass container bind-mounts `/browser` and `/cemba`, so its uwsgi workers block the same way.
- **There's no gcsfuse log of the cause.** SkyPilot started the mounts with output sent to `/dev/null`. The remount below writes to `~/gcsfuse-browser.log` instead.

## Diagnose without hanging your own shell

**Never run `ls`, `df`, `du` or `stat` on a suspect mount.** They block in `D` state just like the app, and `timeout` can't kill them. `du -x /` also hangs, because it stats the mount point.

These checks are safe:

```bash
# Requests the kernel is still waiting on, per gcsfuse mount (non-zero and not draining = frozen)
grep fuse.gcsfuse /proc/self/mountinfo | while read _ _ mm _ mp _; do
  echo "$mp: $(sudo cat /sys/fs/fuse/connections/${mm#*:}/waiting)"; done

# Stuck processes, and where one is blocked
ps -eo pid,ppid,stat,etime,args | awk '$3 ~ /^D/'
sudo cat /proc/<pid>/stack

sudo dmesg -T | grep "blocked for more"
tail ~/error.log; sudo tail /var/log/nginx/error.log
```

## Recovery

Connect with `gcloud compute ssh browser-small-0e06-head-cfxpcfmm-compute --project ecker-bican --zone us-west1-a`. Use the gcloud account that originally deployed the app. Gunicorn, the `deploy` screen session and the gcsfuse mounts all belong to that account's Linux user, and from another user you can't see or stop them.

The example below is for `/browser`. Repeat steps 2–4 for whichever mount shows waiting requests.

1. **Stop gunicorn first,** so the master doesn't start new workers against the broken mount. Find the master with `pgrep -f '[g]unicorn -w 4' -o`, then send it `kill -TERM`. It exits after its 30 s graceful timeout. Its workers may stay in `D`, which is expected.
2. **Abort the dead FUSE connection.** This makes every stuck call fail with `ENOTCONN`, so the stuck processes finally exit.

   ```bash
   minor=$(grep ' /browser ' /proc/self/mountinfo | awk '{print $3}' | cut -d: -f2)
   echo 1 | sudo tee /sys/fs/fuse/connections/$minor/abort
   ps -eo pid,stat,args | awk '$2 ~ /^D/'   # should now be empty
   ```

3. **Unmount** with `fusermount -u /browser || sudo umount -l /browser`. Check that `/browser` is gone from `/proc/mounts` and that the old gcsfuse process has exited. If it hasn't, `kill -TERM` its pid.
4. **Remount** with the same flags SkyPilot uses, but log to a file:

   ```bash
   nohup setsid /usr/bin/gcsfuse --foreground -o allow_other --implicit-dirs \
     --stat-cache-capacity 4096 --stat-cache-ttl 5s --type-cache-ttl 5s --rename-dir-limit 10000 \
     hanqing-wmb-browser /browser > ~/gcsfuse-browser.log 2>&1 < /dev/null &
   ```

   `ls /browser` should list `genome`, `matrix`, `metadata` and `notebooks`, and the log should end with "File system has been successfully mounted."
5. **Restart HiGlass** with `sudo docker restart higlass-container`. The container keeps the old, dead bind mount until it restarts.
6. **Relaunch gunicorn in the `deploy` screen session.** `OPENAI_API_KEY` comes from `~/.bashrc`, so launching in that shell keeps it.

   ```bash
   screen -S deploy -X stuff 'cd ~/wmb-browser/wmb_browser && /opt/conda/bin/gunicorn -w 4 index:server -b 127.0.0.1:8000 --timeout 60 --access-logfile ~/access.log --error-logfile ~/error.log\n'
   ```

### gcsfuse mounts on the VM

| Mount | Bucket | Bind-mounted into HiGlass |
| --- | --- | --- |
| `/browser` | `hanqing-wmb-browser` | yes |
| `/cemba` | `hanqing-wmb-data-us-west1` | yes |
| `/ref` | `hanqing-reference` | no |
| `/home/hanliu` | `hanqing-analysis` | no |

`/home/hanliu` is a bucket mount, not the deploy user's home. Gunicorn's `~/access.log` and `~/error.log` are on local disk in the SSH user's own home.

## Verify

- `tail ~/error.log` shows `Listening at: http://127.0.0.1:8000` and four `Booting worker` lines, with no traceback.
- On the VM, `curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/` and the same for `http://127.0.0.1:8989/api/v1/tilesets/` both return `200`.
- From outside:
  - `https://mousebrain.salk.edu/` and `/dynamic_browser` return `200` in about 0.1 s.
  - `https://mousebrain.salk.edu:8001/api/v1/tilesets/?limit=1` returns JSON. On 2026-10-08 it reported `"count": 2729`.
  - `.../api/v1/tileset_info/?d=<uuid>` for a matrix tileset returns its resolutions, which proves HiGlass can read data files.
- Load a `/dynamic_browser` panel in a real browser.

## Housekeeping done on 2026-10-08

- **nginx logs:** 2.1 MB in total, rotated daily with 14 kept. No action needed.
- **systemd journal:** `sudo journalctl --vacuum-size=500M` freed 3.5 GB of the 4.1 GB. The root disk went from 87% to 84% used.
- **Not yet investigated:** `/var` uses 75 GB and `/tmp` 20 GB. Gunicorn's `~/access.log` (135 MB) and `~/error.log` (22 MB) are never rotated.

## Gotchas

- With `gcloud compute ssh --command "..."`, a `pgrep -f 'X'` also matches the remote shell itself if the literal `X` appears anywhere else in the same command.
- Before a long-running check on the VM, run any probe that might touch a FUSE mount in the background with output to a file. Otherwise one hung call blocks the whole SSH session.
- Over a long uptime (401 days here), `dmesg -T` timestamps drift. Trust the application logs for timing.

## Follow-ups (not done)

- **Upgrade gcsfuse.** 1.3.0 is old, and this hang has happened at least twice (July in `dmesg`, then the August outage).
- **Add an external uptime check** on `https://mousebrain.salk.edu/`. This outage went unnoticed for two months.
- **Rotate gunicorn's `~/access.log` and `~/error.log`.**
