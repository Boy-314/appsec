#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dictionary.h"

// helper method to determine whether or not an input is a number or not
// returns 1 if it is a number, 0 otherwise
bool is_number(const char* word)
{
	for (int i = 0; i < strlen(word); i++) {if (!isdigit(word[i])) {return 0;}}
	return 1;
}

// helper method to detect if a word has non-ascii characters
// returns 1 if there is a non-ascii charecter, 0 otherwise
bool is_ascii(const char* word)
{
	for (int i = 0; i < strlen(word); i++) {if (word[i] > 127 || word[i] < 0) {return 1;}}
	return 0;
}

bool check_word(const char* word, hashmap_t hashtable[])
{
	int bucket = hash_function(word);
	hashmap_t cursor = hashtable[bucket];
	//printf("check_word uppercase\nword: %s\nbucket: %d\n", word, bucket);

	// if the word is a number, return 1
	if(is_number(word)) {return 1;}
	// if the word contains non-ascii characters, return 0;
	if(is_ascii(word)) {return 0;}

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
			//printf("found match: %s\n", word);
			free(lower_case);
			return 1;
		}
		cursor = cursor->next;
	}
	bucket = hash_function(lower_case);
	cursor = hashtable[bucket];
	//printf("\ncheck_word lowercase\nword: %s\nbucket: %d\n", lower_case, bucket);
	while(cursor != NULL)
	{
		if(!strcmp(lower_case, cursor->word))
		{
			//printf("found lower_case match: %s\n", lower_case);
			free(lower_case);
			return 1;
		}
		cursor = cursor->next;
	}
	//printf("found misspelling: %s\n", lower_case);
	free(lower_case);
	return 0;
}

bool load_dictionary(const char* dictionary_file, hashmap_t hashtable[])
{
	for(int i = 0; i < HASH_SIZE; i++) {hashtable[i] = NULL;}
	FILE* dict_file = fopen(dictionary_file,"r");
	hashmap_t new_node;
	if(dict_file == NULL)
	{
		fclose(dict_file);
		return 0;
	}
	char word[LENGTH];
	while(fgets(word, LENGTH, dict_file) != NULL)
	{
		// remove potential whitespace character
		word[strcspn(word, " ")] = 0;
		word[strcspn(word, "\t")] = 0;
		word[strcspn(word, "\n")] = 0;
		word[strcspn(word, "\v")] = 0;
		word[strcspn(word, "\f")] = 0;
		word[strcspn(word, "\r")] = 0;

		// remove quotation marks
		word[strcspn(word, "“")] = 0;
		word[strcspn(word, "”")] = 0;

		new_node = malloc(sizeof(struct node));
		new_node->next = NULL;
		// new_node->word = word;
		strcpy(new_node->word, word);
		int bucket = hash_function(word);
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

// method to remove punctuation from the beginning and end of words
char* remove_punctuation(char* word)
{
	for (; *word && !isalpha(*word); ++word);
	if (*word == '\0') {return word;}
	char* end = word + strlen(word);
	for(; !isalpha(*end); --end);
	*++end = '\0';
	return word;
}

int check_words(FILE* fp, hashmap_t hashtable[], char* misspelled[])
{
	int misspelled_index = 0;
	int num_misspelled = 0;
	char* line = malloc(HASH_SIZE);
	size_t max_length = HASH_SIZE;
	char* line_copy;
	while(getline(&line, &max_length, fp) != -1)
	{
		// todo: free line_copy
		line_copy = strdup(line);
		char* split_line = strtok(line_copy, " ");
		while(split_line != NULL)
		{

			split_line = remove_punctuation(split_line);

			// remove potential whitespace character
			split_line[strcspn(split_line, " ")] = 0;
			split_line[strcspn(split_line, "\t")] = 0;
			split_line[strcspn(split_line, "\n")] = 0;
			split_line[strcspn(split_line, "\v")] = 0;
			split_line[strcspn(split_line, "\f")] = 0;
			split_line[strcspn(split_line, "\r")] = 0;

			// remove directional quotation marks
			split_line[strcspn(split_line, "“")] = 0;
			split_line[strcspn(split_line, "”")] = 0;

			if(check_word(split_line, hashtable) == 0)
			{
				misspelled[misspelled_index] = split_line;
				misspelled_index = misspelled_index + 1;
				num_misspelled = num_misspelled + 1;
			}

			split_line = strtok(NULL, " ");

			// printf("misspelled: ");
			// for (int i = 0; i < misspelled_index; i++) {
			// 	printf("%s, ", misspelled[i]);
			// }
			// printf("\n");

		}
	}
	return num_misspelled;
}
