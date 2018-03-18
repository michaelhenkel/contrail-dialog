#!/bin/bash
tempfile=/tmp/choices
trap "rm $tempfile; exit" SIGHUP SIGINT SIGTERM

_main () {
   dialog --title "Contrail Deployer" \
           --menu "Please choose an option:" 15 55 5 \
                   1 "Edit providers" \
                   2 "Edit config file" \
                   3 "Exit from this menu" 2>$tempfile

   retv=$?
   echo $retv
   choice=$(cat $tempfile)
   echo $choice
   [ $retv -eq 1 -o $retv -eq 255 ] && exit

   case $choice in
       1) dialog --textbox $file 0 0
          _main
           ;;
       2) _edit
          _main ;;
       3) exit ;;
   esac
}

_main

