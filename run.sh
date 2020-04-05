#!/usr/bin/env bash

while :
do
  reset && python oneway.py main
  sleep 200
  reset && python oneway.py vk
  sleep 200
  reset && python oneway.py youtube
  sleep 200
done
