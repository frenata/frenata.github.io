% Dr. Fan (or: How I learned to stop worrying and put everything into a jail)
% Andrew Nichols
% 3 October 2023

## Dilemnas

Having finally secured a new CPU fan for my rapidly-aging-but-still-perfectly-functional laptop, I had a choice to make: what OS to install on it? My needs were pretty simple. Even on a work machine, give me a terminal (preferably Alacritty), a browser (preferably Firefox), and my trusty [.tmux.conf](https://gist.github.com/frenata/d5150712adbe5d4928361f6a991cc1f9) and I'm ready to roll. But beyond [hacking](https://en.wikipedia.org/wiki/Hacker) and [hacking](https://en.wikipedia.org/wiki/Security_hacker) I wanted to expand my own learnings, so I dismissed various flavors of Linux. I determined to go back to the BSDs, never mind that none of them support suspend-on-lid-close. Who needs portability from an allegedly portable device, anyway?

I really wanted to like OpenBSD with its "hardened by default" stance. But more than that I wanted a system I could *describe in code*. The benefits of "throw away and recreate it" systems have been driven home through work: I wanted that for a personal daily driver too. Frankly I'm just [tired](https://www.youtube.com/watch?v=VaMno8d0Tzw&t=12s) of setting/fixing up a system by running a series of adhoc commands. We have better techniques for production, why not better techniques for localhost?

## Questions

A descriptive system: sure sounds like [Nix](https://nixos.org/) or [Guix](https://guix.gnu.org/), right? Or docker? With k8s? Does [bhyve](https://wiki.freebsd.org/bhyve/OpenBSD) do what I want? Oh and whatever I choose, can I easily stand up virtual labs? [FreeBSD Jails](https://docs.freebsd.org/en/books/handbook/jails/#thin-jail) looked quite interesting, but all of the documentation was fundamentally imperative...

Finally I found something that really juiced my interest: Bastille, one of many FreeBSD "jail management" tools, had developed something called a [Bastillefile](https://github.com/BastilleBSD/bastille#bastille-template). Maybe I didn't need to describe the *host* system, if everything other than the basics was running in a version-controlled and described-via-Bastillefile *jail*.

## Trial and Error

I found the documentation a little confusing (it exists in at least three places, isn't always consistent, and doesn't have enough examples), but I persisted. I couldn't get [dynamic redirect](https://github.com/BastilleBSD/bastille#bastille-rdr) to work. I slammed my head against getting TCP connections to a PostgreSQL jail to work for *hours* before I figured out that it was my *hosts*'s `/etc/pf.conf` that was the problem. I destroyed and re-created jails too many times to count, making sure that everything (other than the host `pf.conf`!) was truly reproduceable. I cursed the learning curve on `rc.d` scripting. But I finally got a working 3-tier [toy application](https://github.com/frenata/xanadu) running.

## Interesting Bits

### Parametrized Templates

```
	doas bastille template khan frenata/coleridge/khan --arg db_pass=${DB_PASS}
	doas bastille template kubla-1 frenata/coleridge/kubla --arg db_pass=${DB_PASS}
	doas bastille template kubla-2 frenata/coleridge/kubla --arg db_pass=${DB_PASS}
```

I needed to set a password for my database user *at jail creation time* and hardcoding a thing screamed against all my instincts. Fortunately `Bastillefile`s have a `ARG` command that can accept arbitrary arguments -- which can be used by other commands but critically can be `RENDER`ed into files in the jail. Notably files I'm copying or overlaying (I'm uncertain on the tradeoff here) in.

Thus the application service:

```
kubla_cmd="/usr/local/bin/kubla"
kubla_env="DB_PASS=${db_pass}"
```

and the database bootstrap script:

```
psql -U postgres -c "alter user postgres password '${db_pass}'"
```

can both be `RENDER`ed on jail-disk and specified by the user at orchestration time.

### Daemonizing a Go Binary

This isn't really Bastille specific, but as a FreeBSD-newbie, this was one of the harder things to work out.

```
kubla_cmd="/usr/local/bin/kubla"
pidfile="/var/run/${name}.pid"
command="/usr/sbin/daemon"
command_args="-P ${pidfile} -r -f ${kubla_cmd}"
```

That collectively means: run this binary as a daemon with a controlled PID file, restarting it as needed. The idea is that `service kubla {start, stop, restart}` just works after this.

But you also have to *stop* it properly by killing the daemon itself:

```
stop_postcmd="stop_kubla"
stop_kubla()
{
	if [ -e "${pidfile}" ]; then
		echo "stop daemon"
		kill -s TERM `cat ${pidfile}`
	fi
}
```

Much easier was ensuring the binary was rebuilt on restart: `start_precmd="cd /src && /usr/local/bin/go build -o /usr/local/bin/kubla ."`

I might have given up and done something much hackier without [reddit](https://old.reddit.com/r/freebsd/comments/7nmrha/supervised_freebsd_rcd_script_for_a_go_daemon/), and I'm sure this isn't selling anyone on the glories of `rc.d` over `systemd`. It's... livable.

## Reflection

In the end I accomplished *some* of what I wanted. I had reproduceable services on my host, and hit (and learned from) several FreeBSD-related snags: `pf.conf` and `rc.d`. But I didn't configure my host -- only a set jails for a sample application. I'd gone down a production-oriented path rather than a localhost-oriented one, despite my intentions.

But using (apparently?) the same mechanisms, the excellently named [rocinante](https://github.com/BastilleBSD/rocinante) appears promising, should I choose to stay on the BSD-ish path. Other things irritated me and left me with questions:

  1. Setting up some of these jails was pretty slow due to the large number of dependencies. For instance the `kubla` template is intended to be run as a cluster of servers -- I can imagine auto-scaling this cluster and would want to minimized time from `bastille create` to a running server. Is there an easy way to create layers/checkpoints/bootstraps to save time?
  2. I don't love setting hardcoded IPs. Is there a way to just hand out ranges and let the management system figure it out? In my toy, only one IP/port needed to even be exposed to the host. Ideally I'd want the connectivity between jails also expressed, in a way that means I don't have to learn a bunch of `pf.conf` or do adhoc things on the host.
  3. Is jail startup or dependency [orderable](https://github.com/BastilleBSD/bastille/issues/577)? Or is this an XY question and a properly designed system would be robust to failure?
  4. What about more complex [orchestration](https://github.com/BastilleBSD/bastille/issues/609)? Across hosts? With auto-scaling? While I could hack more stuff together via `Makefile`, it's... not ideal.
  
## Next Up

  * [LinuxJails](https://wiki.freebsd.org/LinuxJails), for things where software doesn't (conveniently) run on FreeBSD?
  * `rocinante`
  * Look at the Nomad/Pot driver and see how easily it could be adapted for `bastille`
  * PR some documentation fixes
