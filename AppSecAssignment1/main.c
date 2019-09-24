#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dictionary.h"

int main(int argc, char* argv[])
{
	if(argc != 3)
	{
		printf("incorrect number of arguments, expected 3");
	} else {
		// get arguments
		char* input_file = argv[1];
		char* dictionary_file = argv[2];

		hashmap_t hashtable[HASH_SIZE];
		char* mispelled[MAX_MISSPELLED];

		// load words into hashmap
		if(load_dictionary(dictionary_file, hashtable))
		{
			FILE* fp = fopen(input_file,"r");
			int count_misspelled = check_words(fp, hashtable, mispelled);
			printf("%d",count_misspelled);
			fclose(fp);
		}
	}
	return 0;
}
