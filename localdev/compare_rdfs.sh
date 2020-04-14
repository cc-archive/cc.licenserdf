#!/bin/bash
set -o errexit
set -o errtrace
set -o nounset

trap '_es=${?};
    printf "${0}: line ${LINENO}: \"${BASH_COMMAND}\"";
    printf " exited with a status of ${_es}\n";
    exit ${_es}' ERR 


OBJECT=${1:-master}
SCOPE=${2:-five_random}

if [[ "${SCOPE}" == all ]]
then
    # All licenses
    RDFS="$(find cc/licenserdf/licenses -maxdepth 1 -type f -name '*.rdf')"
else
    # Random selection of each version
    RDFS="$(
        find cc/licenserdf/licenses -maxdepth 1 -type f -iname '*by*1.0*.rdf' \
            | shuf | head -n1;
        find cc/licenserdf/licenses -maxdepth 1 -type f -iname '*by*2.0*.rdf' \
            | shuf | head -n1;
        find cc/licenserdf/licenses -maxdepth 1 -type f -iname '*by*3.0*.rdf' \
            | shuf | head -n1;
        find cc/licenserdf/licenses -maxdepth 1 -type f -iname '*by*4.0*.rdf' \
            | shuf | head -n1;
        find cc/licenserdf/licenses -maxdepth 1 -type f -iname '*zero*.rdf' \
            | shuf | head -n1;
        )"
fi
for _rdf in ${RDFS}
do
    label_old="$(printf '%-7s:%s' "${OBJECT}" "${_rdf}")"
    label_new="$(printf '%-7s:%s' 'CURRENT' "${_rdf}")"
    git show ${OBJECT}:${_rdf} | sort -o temp_compare_rdfs_old
    sort ${_rdf} -o temp_compare_rdfs_new
    diff=$(diff --unified --minimal --label "${label_old}" \
        --label "${label_new}" \
        temp_compare_rdfs_old temp_compare_rdfs_new \
        || true)
    rm -f temp_compare_rdfs_old temp_compare_rdfs_new
    [[ -n "${diff}" ]] || continue
    printf "\e[1m\e[7m${_rdf}\e[0m\n"
    echo "${diff}" | colordiff
    echo
    echo
done
