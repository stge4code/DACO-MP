It's recommended to add alias to .bashrc file:

dacofun() {
    #do things with parameters like $1 such as
    python /home/mar345/DACO_MP-shell.py "$*"
}
alias okdaco=dacofun