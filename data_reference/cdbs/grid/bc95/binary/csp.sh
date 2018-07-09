#! /bin/sh
# Script csp_galaxev.sh

setenv bc95				/arc1/ftp/pub/charlot/bc95_files

setenv RF_COLORS_ARRAYS                 $bc95/RF_COLORS.cousins
setenv FILTERS				$bc95/FILTERBIN.RES
setenv A0VSED				$bc95/A0V_KUR_BB.SED

$bc95/csp

