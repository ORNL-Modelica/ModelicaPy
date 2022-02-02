RAVEN=./../../../../../../raven/raven_framework

declare -a TESTS
TESTS=(sampleFMU.xml calibrateFMU_noEnsembleModel.xml calibrateFMU_ensembleModel.xml calibrateFMU_ensembleModel_dtw.xml sampleFMU_PP.xml calibrateFMU_RrR.xml sampleFMU_PP_alias.xml calibrateFMU_RrR_alias.xml createROM.xml sampleROM.xml createROM_V.xml sampleROM_V.xml)

NL=$'\n'
NL2=$'\n\n'

nTESTS=${#TESTS[@]}

echo "${NL}Number of tests found = ${nTESTS}${NL}"

mkdir log
#for test in "${TESTS[@]}"
for (( i=0; i<${nTESTS}; i++ ));
do
    iTest=$((i+1))
    echo "${NL}Test (${iTest}/${nTESTS}) Begin: ${TESTS[$i]}"
    $RAVEN ${TESTS[$i]} > "log/${i}_${TESTS[$i]}.log"
    #| tee "log/${i}_${TESTS[$i]}.log"
    echo "Test (${iTest}/${nTESTS}) Completed: ${TESTS[$i]}${NL}"
done