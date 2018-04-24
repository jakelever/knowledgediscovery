# Old Analysis

Here is some old analysis code that wasn't used in the final paper but may be useful.

## Make Predictions for Alzheimer's and Parkinson's Disease

We'll output predictions for Alzheimer's and Parkinson's.

```bash
# Store the CUIDs for Alzheimer's and Parkinson's
echo "C0002395" > cuids.alzheimers.txt
echo "C0030567" > cuids.parkinsons.txt
echo "C0242422" >> cuids.parkinsons.txt

# Use the CUIDs to find the row numbers for each term
grep -nFf cuids.alzheimers.txt umlsWordlist.WithIDs.txt | cut -f 1 -d ':' | awk ' { print $0-1; } ' > ids.alzheimers.txt
grep -nFf cuids.parkinsons.txt umlsWordlist.WithIDs.txt | cut -f 1 -d ':' | awk ' { print $0-1; } ' > ids.parkinsons.txt

# Get all terms that are of type Pharmacologic Substance (T121) or Clinical Drug (T200)
grep -n -P "(T121)|(T200)" umlsWordlist.WithIDs.txt | cut -f 1 -d ':' | awk ' { print $0-1; } ' > ids.drugs.txt

# Filter for those terms that actually appear in the matrix (using the trainingAndValidation.ids file)
grep -xFf finalDataset/trainingAndValidation.ids ids.drugs.txt > ids.drugs.txt.filtered
mv ids.drugs.txt.filtered ids.drugs.txt

# Start calculating scores
python ../analysis/calcSVDScores.py --svdU svd.all.U --svdV svd.all.V --svdSV svd.all.SV --idsFileA ids.alzheimers.txt --idsFileB ids.drugs.txt --sv $optimalSV --threshold $optimalThreshold --outFile predictions.alzheimers.txt

python ../analysis/calcSVDScores.py --svdU svd.all.U --svdV svd.all.V --svdSV svd.all.SV --idsFileA ids.parkinsons.txt --idsFileB ids.drugs.txt --sv $optimalSV --threshold $optimalThreshold --outFile predictions.parkinsons.txt

# Then filter out for only novel discoveries
bash ../combine_data/filterCooccurrences.sh predictions.alzheimers.txt finalDataset/all.ids finalDataset/all.cooccurrences predictions.alzheimers.novel.txt

bash ../combine_data/filterCooccurrences.sh predictions.parkinsons.txt finalDataset/all.ids finalDataset/all.cooccurrences predictions.parkinsons.novel.txt

# Lastly get the actual terms out of the file for the predictions and sort them
cat predictions.alzheimers.novel.txt | awk -v f=umlsWordlist.WithIDs.txt ' BEGIN { x=0; while (getline < f) dict[x++] = $0; } { print $0"\t"dict[$2]; } ' | sort -k3,3gr > predictions.alzheimers.novel.withterms.txt
cat predictions.parkinsons.novel.txt | awk -v f=umlsWordlist.WithIDs.txt ' BEGIN { x=0; while (getline < f) dict[x++] = $0; } { print $0"\t"dict[$2]; } ' | sort -k3,3gr > predictions.parkinsons.novel.withterms.txt

# Clean up
rm predictions.alzheimers.txt predictions.alzheimers.novel.txt
rm predictions.parkinsons.txt predictions.parkinsons.novel.txt

```
