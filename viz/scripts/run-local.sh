if [ -z "${VITE_CLADES_PATH+x}" ]; then
  echo "ERROR: You must define the env variable VITE_CLADES_PATH to point to the location of your clades JSON, relative to the top-level 'results' directory"
  exit 2
fi
if [ -z "${VITE_LINEAGES_PATH+x}" ]; then
  echo "ERROR: You must define the env variable VITE_LINEAGES_PATH to point to the location of your lineages JSON, relative to the top-level 'results' directory"
  exit 2
fi

data_port="4238"

if [[ $1 == 'production' ]]; then
  VITE_DATA_HOST="http://localhost:${data_port}" npm run build
  vite_cmd="npx vite preview"
  info_msg="This is using a production-ready build, which should\nbe fast but doesn't allow you to edit the JavaScript\ncode on-the-fly."
else
  vite_cmd="npx vite"
  info_msg="This is using a development build, which allows\nediting of the JavaScript souce code on-the-fly\nbut is slower than the production build"
fi


# We want to serve JSONs from within the top-level results directory
pushd ../results >/dev/null 2>&1
data_dir=$( pwd )
popd >/dev/null 2>&1


echo ""
echo "---------------------------------------------------------------"
echo "                        Forecasts nCoV                         "
echo ""
echo "Using local JSON files from the top-level results directory"
echo "(${data_dir})"
echo "CLADES:    ${VITE_CLADES_PATH}"
echo "LINEAGES:  ${VITE_LINEAGES_PATH}"
echo ""
echo -e "${info_msg}"
echo ""
echo -e "The address to view the data should be shown below (it is the\nURL ending with /forecasts-ncov)"
echo "---------------------------------------------------------------"
echo ""

  
VITE_DATA_HOST="http://localhost:${data_port}" \
  npx concurrently \
  "npx serve --cors -p 4238 ${data_dir}" \
  "${vite_cmd}"
