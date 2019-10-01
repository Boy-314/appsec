#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dictionary.h"

// helper method to determine whether or not an input is a number or not
// returns 1 if it is a number, 0 otherwise
bool isnumber(const char* word)
{
	for (int i = 0; i < strlen(word); i++)
	{
		if (!isdigit(word[i]))
		{
			return 0;
		}
	}
	return 1;
}

bool check_word(const char* word, hashmap_t hashtable[])
{
	int bucket = hash_function(word);
	hashmap_t cursor = hashtable[bucket];
	//printf("word: %s\ncheck_word bucket: %d\n", word, bucket);

	// if the word is a number, return 1
	if(isnumber(word)) {return 1;}

	// lower_case = lower_case(word)
	const int length = strlen(word);
	char* lower_case = (char*)malloc(length + 1);
	lower_case[length] = 0;
	for(int i = 0; i < length; i++) {lower_case[i] = tolower(word[i]);}

	while(cursor != NULL)
	{
		//printf("\nword: %s\ncursor->word: %s\ncheck_word bucket: %d\n", word, cursor->word, bucket);
		if(!strcmp(word, cursor->word))
		{
			//printf("found misspelling: %s\n", word);
			free(lower_case);
			return 1;
		}
		cursor = cursor->next;
	}
	bucket = hash_function(word);
	cursor = hashtable[bucket];
	while(cursor != NULL)
	{
		if(!strcmp(lower_case, cursor->word))
		{
			//printf("found lower_case misspelling: %s\n", lower_case);
			free(lower_case);
			return 1;
		}
		cursor = cursor->next;
	}
	free(lower_case);
	return 0;
}

bool load_dictionary(const char* dictionary_file, hashmap_t hashtable[])
{
	for(int i = 0; i < HASH_SIZE; i++) {hashtable[i] = NULL;}
	FILE* dict_file = fopen(dictionary_file,"r");
	if(dict_file == NULL)
	{
		fclose(dict_file);
		return 0;
	}
	char word[LENGTH];
	while(fgets(word, LENGTH, dict_file) != NULL)
	{
		// remove potential end line character
		word[strcspn(word, "\n")] = 0;
		hashmap_t new_node = malloc(sizeof(struct node));
		new_node->next = NULL;
		// new_node->word = word;
		strcpy(new_node->word, word);
		int bucket = hash_function(word);
		//printf("word: %s\nload_dictionary bucket: %d\n", word, bucket);
		if(hashtable[bucket] == NULL) {hashtable[bucket] = new_node;}
		else
		{
			new_node->next = hashtable[bucket];
			hashtable[bucket] = new_node;
		}
	}
	fclose(dict_file);
	return 1;
}

// additional method to remove punctuation from a word
void remove_punctuation(char* p)
{
  char* src = p;
	char* dst = p;

    while (*src)
    {
       if (ispunct((unsigned char)*src)) {src++;}
       else if (src == dst)
       {
          src++;
          dst++;
       }
       else {*dst++ = *src++;}
    }

    *dst = 0;
}

int check_words(FILE* fp, hashmap_t hashtable[], char* misspelled[])
{
	int num_misspelled = 0;
	char* line;
	size_t max_length = HASH_SIZE;
	while(getline(&line, &max_length, fp) != -1)
	{
		char* split_line = strtok(line, " ");
		int misspelled_index = 0;
		while(split_line != NULL)
		{
			remove_punctuation(split_line);
			// remove potential end-line character
			split_line[strcspn(split_line, "\n")] = 0;
			if(!check_word(split_line, hashtable))
			{
				misspelled[misspelled_index] = split_line;
				misspelled_index = misspelled_index + 1;
				num_misspelled = num_misspelled + 1;
			}
			split_line = strtok(NULL, " ");
		}
	}
	return num_misspelled;
}
