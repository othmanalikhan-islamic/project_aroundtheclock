#!/bin/bash


@test "Check python3 dependency installed" {
  run dpkg -s python3 &> /dev/null
  [ "$status" -eq 0 ]

  run dpkg -s python3-pip &> /dev/null
  [ "$status" -eq 0 ]

  run dpkg -s python3-venv &> /dev/null
  [ "$status" -eq 0 ]
}


@test "Check network library dependency installed" {
  run dpkg -s dsniff &> /dev/null
  [ "$status" -eq 0 ]
}


@test "Check python virtual environment created" {
  run ls virtual/
  [ "$status" -eq 0 ]
}


@test "Check aroundtheclock user exists" {
  result=$(cat /etc/passwd | grep -c aroundtheclock)
  [ "$result" -eq 1 ]
}


@test "Check aroundtheclock user is assigned no default shell" {
  result=$(cat /etc/passwd | grep -c aroundtheclock:/bin/false)
  [ "$result" -eq 1 ]
}


@test "Check aroundtheclock.service exists" {
  run systemctl status aroundtheclock.service > /dev/null
  [ "$status" -ne 4 ]
}


@test "Check aroundtheclock.service is running" {
  run systemctl status aroundtheclock.service > /dev/null
  [ "$status" -eq 0 ]
}


@test "Check aroundtheclock.service enabled at boot" {
  result=$(systemctl list-unit-files | grep aroundtheclock | grep -c enabled)
  [ "$result" -eq 1 ]
}
