osascript - "$@" <<EOF
on run argv

set alList to {"rr", "ra", "ll", "lc", "ch"}

###############
# Starts Server
###############

tell application "iTerm"
    activate
    set new_term_1 to (create window with default profile)
    tell current session of current window
        set name to "cloudlab1"
        write text "ssh cloudlab1"
        write text "pkill -u Impetus python3"
        write text "cd repo"
        write text "python3 server.py -p 50505 -hs 155.98.36.130 >> log.txt"
    end tell
end tell
tell application "iTerm"
    activate
    set new_term_2 to (create window with default profile)
    tell current session of current window
       set name to "cloudlab2"
       write text "ssh cloudlab2"
       write text "pkill -u Impetus python3"
       write text "cd repo"
       write text "python3 server.py -p 50505 -hs 155.98.36.129 >> log.txt"
    end tell
end tell
tell application "iTerm"
    activate
    set new_term_3 to (create window with default profile)
    tell current session of current window
       set name to "cloudlab3"
       write text "ssh cloudlab3"
       write text "pkill -u Impetus python3"
       write text "cd repo"
       write text "python3 server.py -p 50505 -hs 155.98.36.131 >> log.txt"
    end tell
end tell
  
delay 5  

repeat with algorithm in alList
    #####################
    # Starts LoadBalancer
    #####################

    delay 2

    tell application "iTerm"
        activate
        set new_term_0 to (create window with default profile)
        tell current session of current window
           set name to "cloudlab0"
           write text "ssh cloudlab0"
           write text "pkill -u Impetus python3"
           write text "cd repo"
           write text "rm *latency.txt"
           write text "python3 loadbalancer.py -hs 155.98.36.127 -hd " & algorithm & " >> log.txt"
        end tell
    end tell

    ###############
    # Starts Client
    ###############

    delay 2

    tell application "iTerm"
        activate
        set new_term_cl to (create window with default profile)
        tell current session of current window
            set name to "Client"
            write text "cd /Users/Jim/Documents/Project/CSE222A/repo"
            write text "python client.py"
            write text "mv extra.txt " & algorithm & "_extra.txt"
            # write text "exit"
        end tell
    end tell

    #####################
    # Close LB and Client
    #####################

    delay 70

    tell application "iTerm"
      tell current session of new_term_cl
          write text "scp cloudlab0:repo/latency.txt ."
          write text "mv latency.txt " & algorithm & "_latency.txt"
          delay 10
      end tell
      tell new_term_0 to close current session
      tell new_term_cl to close current session
  end tell

    delay 2

end repeat

tell application "iTerm"
    activate
    tell new_term_1 to close current session
    tell new_term_2 to close current session
    tell new_term_3 to close current session
end tell

end run
EOF

