
#include <iomanip>
#include <locale>
#include <sstream>
#include <fstream>

#define min(a,b) (a<b ? (a) : (b))
#define max(a,b) (a>b ? (a) : (b))

std::vector<std::string> &split(const std::string &s, char delim, std::vector<std::string> &elems) {
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}


std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, elems);
    return elems;
}

std::unordered_map<std::tuple<int,int>,int> loadCooccurrences(const char* filename)
{		
	FILE* f = fopen(filename, "r");
	std::unordered_map<std::tuple<int,int>,int> data;

	while (!feof(f)) 
	{
		int x,y,count;
		
		fscanf(f, "%d %d %d", &x, &y, &count);
		
		if (x==y)
		{
			fprintf(stderr, "ERROR: Matrix should have non-zero diagonals\n");
			exit(255);
		}
		else if (x < 0 || y < 0)
		{
			fprintf(stderr, "ERROR: Matrix contains coordinate outside expected dimensions. (%d,%d) < 0\n", x, y);
			exit(255);
		}
		else if (count <= 0)
		{
			fprintf(stderr, "ERROR: Counts are expected to be greater than zero. (%d) < 0\n", count);
			exit(255);
		}
		
		auto key = std::make_tuple ( min(x,y), max(x,y) );
		data[key] = count;
	}
	fclose(f);
	
	return data;
}

std::unordered_map<int,int> loadOccurrences(const char* filename)
{		
	FILE* f = fopen(filename, "r");
	std::unordered_map<int,int> data;

	while (!feof(f)) 
	{
		int x,count;
		
		fscanf(f, "%d %d", &x, &count);
		
		if (x < 0)
		{
			fprintf(stderr, "ERROR: Matrix contains coordinate outside expected dimensions. (%d) < 0\n", x);
			exit(255);
		}
		else if (count <= 0)
		{
			fprintf(stderr, "ERROR: Counts are expected to be greater than zero. (%d) < 0\n", count);
			exit(255);
		}
		
		data[x] = count;
	}
	fclose(f);
	
	return data;
}

std::unordered_set<int> loadVectorsToCalculate(const char* filename)
{		
	FILE* f = fopen(filename, "r");
	std::unordered_set<int> data;

	while (!feof(f)) 
	{
		int x;
		
		fscanf(f, "%d", &x);
		
		if (x < 0)
		{
			fprintf(stderr, "ERROR: Matrix contains coordinate outside expected dimensions. (%d) < 0\n", x);
			exit(255);
		}
		
		data.insert(x);
	}
	fclose(f);
	
	return data;
}