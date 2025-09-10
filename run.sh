#!/usr/bin/env bash

# Script to set up and run the expense tracker with Docker Compose

# Function to print colored output
print_color() {
  local color=$1
  local text=$2
  
  case $color in
    "green") echo -e "\033[0;32m${text}\033[0m" ;;
    "red") echo -e "\033[0;31m${text}\033[0m" ;;
    "yellow") echo -e "\033[0;33m${text}\033[0m" ;;
    "blue") echo -e "\033[0;34m${text}\033[0m" ;;
    *) echo "$text" ;;
  esac
}

# Function to check if a file exists
check_file() {
  if [ ! -f "$1" ]; then
    print_color "red" "Error: File $1 does not exist!"
    return 1
  fi
  return 0
}

# Check if .env file exists
if [ ! -f ".env" ]; then
  print_color "yellow" "No .env file found. Creating one from .env.docker..."
  
  # Check if .env.docker exists
  if [ ! -f ".env.docker" ]; then
    print_color "red" "Error: .env.docker template not found!"
    exit 1
  fi
  
  # Copy the template
  cp .env.docker .env
  print_color "green" ".env file created. Please edit it to set your bot token and other settings."
  print_color "blue" "You can run this script again after editing the .env file."
  exit 0
fi

# Start Docker Compose
print_color "blue" "Starting Docker Compose services..."
docker compose up --build -d

# Check if services started successfully
if [ $? -eq 0 ]; then
  print_color "green" "Services started successfully!"
  print_color "blue" "To view logs: docker compose logs -f"
  print_color "blue" "To stop services: docker compose down"
else
  print_color "red" "Failed to start services. Check the error messages above."
fi
