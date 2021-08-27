#!/bin/bash
rm -f $LABTAINER_DIR/labpacks/testpack.labpack
cd $LABTAINER_DIR/MakepackUI/bin
./buildUI2.sh 
sleep 5
cd $LABTAINER_DIR/scripts/labtainer-student
SimLab.py -vv MakepackUI
# use diff to compare new labpack to expected results
DIFF=$(diff $LABTAINER_DIR/labpacks/testpack.labpack $LABTAINER_DIR/testsets/makepack/expected/testpack.labpack)
echo $DIFF
if [ -z "$DIFF" ]
then
      echo "Sucessful"
else
      echo "Not Successful"
fi
