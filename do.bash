sdir=slides
#subj=hg2052
pushd .
cd $sdir
for slide in `ls lec-*.tex tut-*.tex`
do
    base=`basename $slide .tex`
    echo Processing ${base}
    latexmk -xelatex ${base}
    ## clean up
    #rm *.aux *.bbl *.blg *.log *~ *.dvi *.ps *.pdf
done
popd

### copy changed slides
rsync -avc slides/*.pdf docs/pdf

#htmldoc  --duplex --color --fontsize 12 --webpage -f /home/bond/papers/Outlines/${subj}-outline.pdf www/index.html


echo
echo Updated all slides: check the index.html is up to date
echo
echo Please commit any changes
echo
echo 
git status
echo
