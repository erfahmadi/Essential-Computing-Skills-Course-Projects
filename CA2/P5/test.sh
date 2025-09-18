#!/bin/bash

make

gcc -o reader reader.c
gcc -o writer writer.c

sudo rmmod LIFO_Driver 2> /dev/null

sudo insmod LIFO_Driver.ko

sudo rm -f /dev/lifo_read /dev/lifo_write

MAJOR=$(grep lifo /proc/devices | awk '{print $1}')
sudo mknod /dev/lifo_read c $MAJOR 0; 
sudo mknod /dev/lifo_write c $MAJOR 1; 
sudo chmod 666 /dev/lifo_read /dev/lifo_write

echo "------------------------------------------------------------"

echo -e "\e[1;32mCorrect write and read:\e[0m"
./writer /dev/lifo_write "Hello"
./writer /dev/lifo_write "World"
./reader /dev/lifo_read

echo "------------------------------------------------------------"

echo -e "\e[1;32mRead from empty lifo:\e[0m"
./reader /dev/lifo_read

echo "------------------------------------------------------------"

echo -e "\e[1;32mRead from write-only:\e[0m"
./reader /dev/lifo_write

echo "------------------------------------------------------------"

echo -e "\e[1;32mWrite to read-only:\e[0m"
./writer /dev/lifo_read "Hello"

echo "------------------------------------------------------------"

make clean





