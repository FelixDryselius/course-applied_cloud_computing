#Run this file on workers that will connect to MariaDB backend
#Information regarding host, database, user, and path to files
export DB_HOST_ADDRESS=130.238.28.158
export DB_DATABASE_NAME=test_insert
export DB_USER_WORKER=worker@130.238.28.158
export PATH_TO_WORKER_RESULTS=/home/fenics/shared/murtazo/navier_stokes_solver/results
#Password for 'DB_USER'
export DB_PASSWORD_WORKER=banankaka1
#echo "Please enter Password for DB_USER: $DB_USER "
#read -sr DB_USER_PASSWORD_INPUT
#export DB_PASSWORD_WORKER=$DB_USER_PASSWORD_INPUT
