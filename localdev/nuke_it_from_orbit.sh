#!/bin/bash
set -o errexit
set -o errtrace
set -o nounset

trap '_es=${?};
    printf "${0}: line ${LINENO}: \"${BASH_COMMAND}\"";
    printf " exited with a status of ${_es}\n";
    exit ${_es}' ERR 


rm_directory() {
    local _dir="${1}"
    [[ -d "${_dir}" ]] || return 0
    echo "# removing dir: ${_dir}"
    rm -rf "${_dir}"
}

rm_directory bin/
rm_directory build/
rm_directory cc.licenserdf.egg-info/
rm_directory develop-eggs/
rm_directory dist/
rm_directory eggs/
rm_directory include/
rm_directory lib/
rm_directory local/
rm_directory man/
rm_directory parts/
rm_directory share/

echo '# removing pip environment'
pipenv --rm || true

for _dir in ~/.cache/pipenv ~/Library/Caches/pipenv
do
    if [[ -d "${_dir}" ]]
    then
        echo '# removing pipenv cache directory'
        echo "# ${_dir}"
        rm -rf "${_dir}"
    fi
done
