kill -9  $(nvidia-smi -g 0 | awk '$5=="PID" {p=1} p {print $5}')
kill -9  $(nvidia-smi -g 1 | awk '$5=="PID" {p=1} p {print $5}')
kill -9  $(nvidia-smi -g 2 | awk '$5=="PID" {p=1} p {print $5}')
kill -9  $(nvidia-smi -g 3 | awk '$5=="PID" {p=1} p {print $5}')
kill -9  $(nvidia-smi -g 4 | awk '$5=="PID" {p=1} p {print $5}')
kill -9  $(nvidia-smi -g 5 | awk '$5=="PID" {p=1} p {print $5}')
kill -9  $(nvidia-smi -g 6 | awk '$5=="PID" {p=1} p {print $5}')