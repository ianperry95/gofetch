if set -q CLAUDE_CODE_SESSION_ID; return; end

if status is-interactive; and test -t 0
    if [ -n "$SSH_CLIENT" ]; or [ -n "$SSH_TTY" ]
        set -gx ZELLIJ_AUTO_EXIT    "true"
        set -gx ZELLIJ_AUTO_ATTACH  "true"
        eval (zellij setup --generate-auto-start fish | string collect)
    end
    starship init fish | source

    if not set -q SSH_AGENT_PID; or not kill -0 $SSH_AGENT_PID 2>/dev/null
        eval (ssh-agent -c)
    end
 
    if test -f /proc/version; and string match -q "*microsoft*" (cat /proc/version)
	set -x SSH_AUTH_SOCK $HOME/.ssh/agent.sock
	if not test -S $SSH_AUTH_SOCK
        rm -f $SSH_AUTH_SOCK
        setsid socat UNIX-LISTEN:$SSH_AUTH_SOCK,fork EXEC:"npiperelay.exe -ei -s //./pipe/openssh-ssh-agent",nofork &
    	end
    end

    if string match -q "/mnt/c/*" "$PWD"
        cd ~
    end
end

# Replicate bash !!
abbr -a !! --position anywhere --function last_history_item

function last_history_item
    echo $history[1]
end

function __tabby_working_directory_reporting --on-event fish_prompt
    echo -en "\e]1337;CurrentDir=$PWD\x7"
end
