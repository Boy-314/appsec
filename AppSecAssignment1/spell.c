#include <ctype.h>
#include "dictionary.h"

bool check_word(const char* word, hashmap_t hashtable[])
{
	int bucket = hash_function(word);
	hashmap_t cursor = hashmap[bucket];
	while(cursor != NULL)
	{
		const int length = strlen(word);
		char* lower_case = (char*)malloc(length + 1);
		lower_case[length] = 0;
		for(int i = 0; i < length; i++)
		{
			lower[i] = tolower(word[i]);
		}
		if(word == cursor->word)
		{
			return 1;
		}
		else if(lower_case == cursor->word)
		{
			return 1;
		}
		cursor = cursor->next;
	}
	return 0;
}
bool load_dictionary(const char* dictionary_file, hashmap_t hashtable[]);
int check_words(FILE* fp, hashmap_t hashtable[], char* misspelled[]);