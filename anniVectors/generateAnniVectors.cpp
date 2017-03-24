#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <math.h>

#include <tuple>
#include <vector>
//#include <map>
#include <unordered_map>
#include <unordered_set>
#include <set>
#include <iostream>
#include <string>
#include <string.h>

#include <iomanip>
#include <locale>
#include <sstream>

#include <omp.h>

#include <algorithm>
#include <tclap/CmdLine.h>

#include "tuple_key_fix.h"
#include "dataload.h"

#define min(a,b) (a<b ? (a) : (b))
#define max(a,b) (a>b ? (a) : (b))

double H1(int i, 
		std::unordered_map<int,int> *occurrences, 
		int sentenceCount)
{
	double N_i = (double)(*occurrences)[i];
	double N = (double)sentenceCount;
	double score = -(N_i/N) * log(N_i/N) - ((N-N_i)/N) * log((N-N_i)/N);
	return score;
}

double H2(int i, int j, 
		std::unordered_map<std::tuple<int,int>,int> *cooccurrences,
		std::unordered_map<int,int> *occurrences,
		int sentenceCount)
{
	auto key = std::make_tuple ( min(i,j), max(i,j) );

	double N_ij = 0.0f;
	if (cooccurrences->count(key) > 0)
		N_ij = (double)(*cooccurrences)[key];
		
	double N_i = (double)(*occurrences)[i];
	double N_j = (double)(*occurrences)[j];
	double N = (double)sentenceCount;

	double score = 0.0;
	if (N_ij != 0)
		score += -(N_ij/N) * log(N_ij/N);
	if ((N_j-N_ij) != 0)
		score += - ((N_j-N_ij)/N) * log((N_j-N_ij)/N);
	if ((N_i-N_ij) != 0)
		score += - ((N_i-N_ij)/N) * log((N_i-N_ij)/N);
	if ((N-N_j-N_i) != 0)
		score += - ((N-N_j-N_i)/N) * log((N-N_j-N_i)/N);

	return score;
}

double U(int i, int j, 
		std::unordered_map<std::tuple<int,int>,int> *cooccurrences,
		std::unordered_map<int,int> *occurrences,
		int sentenceCount)
{
	double H_i = H1(i,occurrences,sentenceCount);
	double H_j = H1(j,occurrences,sentenceCount);

	double H_i_j = H2(i,j,cooccurrences,occurrences,sentenceCount);

	double numerator = H_i + H_j - H_i_j;
	double denominator = 0.5 * (H_i + H_j);

	double score = 0.0;
	if (denominator != 0)
		score = numerator/denominator;

	/*if (i==1153)
	{

		auto key = std::make_tuple ( min(i,j), max(i,j) );

		int cooccurrence_ij = 0.0f;
		if (cooccurrences->count(key) > 0)
			cooccurrence_ij = (*cooccurrences)[key];
		int occurrence_i = (*occurrences)[i];
		int occurrence_j = (*occurrences)[j];

		//printf("DEBUG\t%d\t%d\t%d\t%d\t%d\t%f\n",i,j,occurrence_i,occurrence_j,cooccurrence_ij,score);
	}*/
	
	//printf("H2score=%f numerator=%f denominator=%f\n", H2score,numerator,denominator);

	return score;
}

int main(int argc, char** argv)
{
	try 
	{
		TCLAP::CmdLine cmd("Calculates an ANNI curve given occurrence and cooccurrence data", ' ', "1.0");
		
		//TCLAP::ValueArg<int> argDim("","dim","Dimension of the square matrix",true,0,"integer",cmd);
		
		TCLAP::ValueArg<std::string> argCooccurrenceData("","cooccurrenceData","BLAH",true,"","string",cmd);
		TCLAP::ValueArg<std::string> argOccurrenceData("","occurrenceData","BLAH",true,"","string",cmd);
		TCLAP::ValueArg<int> argSentenceCount("","sentenceCount","BLAH",true,0,"integer",cmd);
		
		TCLAP::ValueArg<std::string> argVectorsToCalculate("","vectorsToCalculate","BLAH",true,"","string",cmd);
				
		TCLAP::ValueArg<std::string> argOutIndex("","outIndexFile","BLAH",true,"","string",cmd);
		TCLAP::ValueArg<std::string> argOutVector("","outVectorFile","BLAH",true,"","string",cmd);

		
		//TCLAP::ValueArg<std::string> argOccurrenceData("","occurrenceData","BLAH",true,"","string",cmd);
		
		//TCLAP::ValueArg<std::string> argOutfile("","outFile","Path to file to contain curve points",true,"","string",cmd);
		
		cmd.parse( argc, argv );
		
		int sentenceCount = argSentenceCount.getValue();
				
		const char *outIndexFilename = argOutIndex.getValue().c_str();
		const char *outVectorFilename = argOutVector.getValue().c_str();
		
		printf("generateAnniVectors v1.0\n\n");
		
		//int *cooccurrenceData, trainSize;
		//loadSymmetricTextCoords(argCooccurrenceData.getValue().c_str(), &trainCoords, &trainSize, dim);
		printf("Loading cooccurrence data...\n");
		std::unordered_map<std::tuple<int,int>,int> cooccurrences = loadCooccurrences(argCooccurrenceData.getValue().c_str());
		printf("%lu cooccurrences loaded\n", cooccurrences.size());
		
		printf("Loading occurrence data...\n");
		std::unordered_map<int,int> occurrences = loadOccurrences(argOccurrenceData.getValue().c_str());
		printf("%lu occurrences loaded\n", occurrences.size());
		
		printf("Loading vectors to calculate..\n");
		std::unordered_set<int> vectorsToCalculate = loadVectorsToCalculate(argVectorsToCalculate.getValue().c_str());
		printf("%lu vectors to calculate loaded\n", vectorsToCalculate.size());
		
		printf("Converting sets to arrays for use with OpenMP..\n");
		int vectorsToCalculate_array_size = vectorsToCalculate.size();
		int *vectorsToCalculate_array = (int*)malloc(vectorsToCalculate_array_size * sizeof(int));
		std::copy(std::begin(vectorsToCalculate), std::end(vectorsToCalculate), vectorsToCalculate_array);
		
		std::unordered_set<int> tmpSeen;
		for ( auto it = cooccurrences.begin(); it != cooccurrences.end(); ++it )
		{
			std::tuple<int,int> t = it->first;
			tmpSeen.insert(std::get<0>(t));
			tmpSeen.insert(std::get<1>(t));
		}
		
		int seen_size = tmpSeen.size();
		int *seen = (int*)malloc(seen_size * sizeof(int));
		{
			int i = 0;
			for ( auto it = tmpSeen.begin(); it != tmpSeen.end(); ++it )
				seen[i++] = *it;
		}
		printf("Conversion complete\n");
		
		printf("Sorting lists...\n");
		std::sort(vectorsToCalculate_array, vectorsToCalculate_array + vectorsToCalculate_array_size);
		std::sort(seen, seen + seen_size);
		printf("Sorting complete\n");
	
		
		FILE *outIndexFile = fopen(outIndexFilename, "w");
		FILE *outVectorFile = fopen(outVectorFilename, "w");
		//const char *outFilename = argOutfile.getValue().c_str();
		//for ( auto it1 = vectorsToCalculate.begin(); it1 != vectorsToCalculate.end(); ++it1 )
		
		printf("vectorsToCalculate_array_size=%d\n",vectorsToCalculate_array_size);
		printf("seen_size=%d\n",seen_size);
		
		double *allTmpData = (double*)malloc(omp_get_max_threads()*seen_size*sizeof(double));

		float *buffer = (float*)malloc(seen_size*sizeof(float));
		
		int complete = 0;
		#pragma omp parallel for
		for ( int i=0; i<vectorsToCalculate_array_size; i++ )
		{
			double *tmpData = &allTmpData[seen_size*omp_get_thread_num()];
			//int v1 = *it1;
			int v1 = vectorsToCalculate_array[i];
			//for ( auto it2 = occurrences.begin(); it2 != occurrences.end(); ++it2 )
		
			double norm2 = 0;
			//fprintf(outIndexFile,"%d\n", v1);
			for ( int j=0; j<seen_size; j++ )
			{
				//int v2 = it2->first;
				int v2 = seen[j];
				
				//auto key = std::make_tuple (v1,v2);
				
				
				
				double Uvalue = U(v1,v2, &cooccurrences, &occurrences, sentenceCount);
				
				//printf("%d\t%d\t%f\n", v1, v2, Uvalue);
				
				//auto key = std::make_tuple ( min(v1,v2), max(v1,v2) );
				//printf("%d\t%d\t%f\t\t%d\t%d\t%d\t%d\n", v1, v2, Uvalue, cooccurrences[key], occurrences[v1], occurrences[v2], sentenceCount);
				//fprintf(outVectorFile, "%f ", Uvalue);
				
				tmpData[j] = Uvalue;

				norm2 += Uvalue*Uvalue;
			}

			int normalize = 0;

			if (normalize == 1)
			{
				double norm = sqrt(norm2);
				for ( int j=0; j<seen_size; j++ )
					tmpData[j] /= norm;
			}
			//fprintf(outVectorFile, "\n");
			
			#pragma omp critical
			{
				if ((complete%1000)==0)
				{
					time_t rawtime;
					struct tm * timeinfo;
					char timebuffer[256];

					time (&rawtime);
					timeinfo = localtime (&rawtime);
					strftime(timebuffer, sizeof(timebuffer), "%a %b %d %H:%M:%S %Y", timeinfo);
					printf("%s : %d / %d\n", timebuffer, complete, vectorsToCalculate_array_size);
				}
				
				for ( int j=0; j<seen_size; j++ )
					buffer[j] = (float)tmpData[j];

				fprintf(outIndexFile,"%d\n", v1);
				//fwrite(tmpData, sizeof(double), seen_size, outVectorFile);
				fwrite(buffer, sizeof(float), seen_size, outVectorFile);
				complete++;
			}
			
			//break;
		}
		
		fclose(outIndexFile);
		fclose(outVectorFile);
		
		//free(vectorsToCalculate_array);
		//free(seen);
	} 
	catch (TCLAP::ArgException &e)  // catch any exceptions
	{ 
		std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
		return 255;
	}
	return 0;
}
