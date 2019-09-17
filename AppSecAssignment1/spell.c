#include <ctype.h>
#include "dictionary.h"

bool check_word(const char* word, hashmap_t hashtable[])
{
	int bucket = hash_function(word);
	hashmap_t cursor = hashmap[bucket];
	while(cursor != NULL)
	{
		char* lower_case;
		if(word == cursor->word)
		{
			return 1;
		}
		// TODO: else if lower case of word = cursor->word, return 1
		cursor = cursor->next;
	}
	return 0;
}
bool load_dictionary(const char* dictionary_file, hashmap_t hashtable[]);
int check_words(FILE* fp, hashmap_t hashtable[], char* misspelled[]);