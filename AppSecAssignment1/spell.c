#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include "dictionary.h"

bool check_word(const char* word, hashmap_t hashtable[])
{
	int bucket = hash_function(word);
	hashmap_t cursor = hashmap[bucket];
	while(cursor != NULL)
	{
		// char* lower_case = lower_case(word)
		const int length = strlen(word);
		char* lower_case = (char*)malloc(length + 1);
		lower_case[length] = 0;
		
		for(int i = 0; i < length; i++) {lower[i] = tolower(word[i]);}
		if(word == cursor->word) {return 1;}
		else if(lower_case == cursor->word) {return 1;}
		cursor = cursor->next;
	}
	return 0;
}

bool load_dictionary(const char* dictionary_file, hashmap_t hashtable[])
{
	for(auto i : hashtable[]) {i = NULL;}
	FILE* dict_file = fopen(dictionary_file,"r");
	if(dict_file == NULL) {return 0;}
	char* word[LENGTH];
	while(fgets(word, LENGTH, dict_file) != NULL)
	{
		hashmap_t new_node;
		new_node->next = NULL;
		new_node->word = word;
		int bucket = hash_function(word);
		if(hashtable[bucket] == NULL) {hashtable[bucket] = new_node;}
		else
		{
			new_node->next = hashtable[bucket];
			hashtable[bucket] = new_node;
		}
	}
	fclose(file);
}

// additional method to remove punctuation from a word
void remove_punctuation(char* p)
{
    char* src = p;
	char* dst = p;

    while (*src)
    {
       if (ispunct((unsigned char)*src))
       {
          src++;
       }
       else if (src == dst)
       {
          src++;
          dst++;
       }
       else
       {
          *dst++ = *src++;
       }
    }

    *dst = 0;
}

int check_words(FILE* fp, hashmap_t hashtable[], char* misspelled[])
{
	int num_misspelled = 0;
	char* line[MAX_SIZE];
	while(fgets(line, MAX_SIZE, fp) != NULL)
	{
		char* split_line = strtok(line, " ");
		int misspelled_index = 0;
		for(auto word : split_line)
		{
			word = remove_punctuation(word);
			if(!check_word(word))
			{
				misspelled[misspelled_index] = word;
				misspelled_index = misspelled_index + 1;
				num_misspelled = num_misspelled + 1;
			}
		}
	}
	return num_misspelled;
}