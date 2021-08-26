#!/bin/bash
cd $LABTAINER_DIR/scripts/labtainer-student
rm -f $LABTAINER_DIR/labpacks/testpack.labpack
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
