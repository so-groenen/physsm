#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define BUFF_LEN 256U
#define RADIX 10L
#define VECTOR_CAPACITY 20UL

typedef struct Vec
{
    float* data;
    size_t size;
    size_t capacity;
} Vector;

bool vector_allocate(Vector* vec, size_t capacity);
void vector_destroy(Vector* vec);
bool vector_push(Vector* vec, float val);
bool vector_fill_from_str(Vector* vec, char* buffer, const char* delim);
void remove_line_break(char* line);
void trim(char* line);
bool set_key_value(const char* line, char* key, char* value, const char* delim, size_t len);

int main(int argc, char* argv[])
{
    if (argc <2)
    {
        fprintf(stderr,"Error: Usage: test.exe parameter.txt\n");
        return EXIT_FAILURE;
    }
    puts("Hello from C! Reading parameter file:");

    char key[BUFF_LEN];
    char value[BUFF_LEN];
    const char* delim = ":";
    char outputfile_name[BUFF_LEN];

    size_t length             = 0;
    size_t monte_carlo_trials = 0;

    Vector vec = {0};
    if(!vector_allocate(&vec, VECTOR_CAPACITY))
    {
        fprintf(stderr, "Allocation fail!");
        return EXIT_FAILURE;
    }
    
    FILE* file = fopen(argv[1],"r");
    char line[BUFF_LEN];

    char test[] = "     hahaha      ";
    while (fgets(line, BUFF_LEN, file))
    {
        remove_line_break(line);
        puts(line);

        if(!set_key_value(line, key, value, delim, BUFF_LEN))
        {
            fprintf(stderr, "Could not parse line: %s\n", line);
        }
        if (strcmp(key, "outputfile") == 0)
        {
            strcpy(outputfile_name, value);
        }
        if (strcmp(key, "length") == 0)
        {
            length = strtoul(value, NULL, RADIX);
        }
        if (strcmp(key, "monte_carlo_trials") == 0)
        {
            monte_carlo_trials = strtoul(value, NULL, RADIX);
        }
        if (strcmp(key, "temperature") == 0)
        {
            const char* num_delim = ",";
            char tokens[BUFF_LEN];
            strncpy(tokens, value, BUFF_LEN);
            if(!vector_fill_from_str(&vec, tokens, num_delim))
            {
                fprintf(stderr, "Could not fill vector");
                return EXIT_FAILURE;
            }
        }
    }
    fclose(file);


    size_t N_temp = vec.size;
    float start   = vec.data[0];
    float last    = vec.data[N_temp-1];
    printf(">> Performing Mock experiment using length=%zu with trials=%zu with %zu temps from %.2f to %.2f. \n",
                length, monte_carlo_trials, N_temp, start, last);

    printf(">> Saving mock results in \"%s\".\n", outputfile_name);
    
    FILE* outputfile = fopen(outputfile_name, "w");
    fprintf(outputfile, "Hello from C!\n");
    fprintf(outputfile, "result1 => %.2f\n", (float)length + 0.42f);
    fprintf(outputfile, "result2 => %.2f\n", (float)monte_carlo_trials + 0.42f);

    fclose(outputfile);
    vector_destroy(&vec);
    return EXIT_SUCCESS;
}


bool vector_allocate(Vector* vec, size_t capacity)
{
    float* data = calloc(capacity, sizeof(float));
    if (data == NULL)
    {
        return false;
    }
    
    *vec = (Vector){
        .data     = data,
        .size     = 0,
        .capacity = capacity,
    };
    return true;
}

void vector_destroy(Vector* vec)
{
    free(vec->data);
    vec->data = NULL;
}

bool vector_push(Vector* vec, float val)
{
    if (vec->size == vec->capacity)
    {
        float* data = realloc(vec->data, 2UL * vec->capacity * sizeof(float));
        if (data == NULL)
        {
            vector_destroy(vec);
            return false;
        }
        vec->capacity *= 2;
        vec->data      = data;
    }
    vec->data[vec->size] = val;
    vec->size++;
    return true;
}


void remove_line_break(char* line)
{
    size_t n = strcspn(line, "\n");
    if (n < SIZE_MAX)
    {
        line[n] = '\0';
    }
}

void trim_left(char* line)
{
    size_t start = 0;
    while (strchr(line + start, ' ') == line + start)
    {
        start++;      
    }
    if (start == 0)
        return;

    if (start == strlen(line) - 1)
    {
        line[0] = '\0';
        return;           
    }
    
    memmove(line, line + start, strlen(line) - start);
    line[strlen(line) - start] = '\0';           
}
void trim_right(char* line)
{
    char* last = NULL;
    while ((last = strrchr(line, ' ')) == line + strlen(line) - 1)
    {
        *last = '\0';     
    } 
}
void trim(char* line)
{
    trim_left(line);
    trim_right(line);
}
bool set_key_value(const char* line, char* key, char* value, const char* delim, size_t len)
{
    size_t n = strcspn(line, delim);
    if (n == SIZE_MAX)
    {
        return false;
    }

    memset(key, '\0', len);
    memset(value, '\0', len);

    strncpy(key, line, n);
    key[n] = '\0';
    trim(key);
    
    strncpy(value, line+n+1, strlen(line+n+1));
    trim(value);
    return true;
}


// vv this performs a destructive tokenization of "buffer", consider copying the data first...
bool vector_fill_from_str(Vector* vec, char* buffer, const char* delim) 
{
    char* num_str    = strtok(buffer, delim);
    char* error_char = NULL;
    while (num_str != NULL)
    {   
        float num = strtof(num_str, &error_char);
        if (error_char != num_str + strlen(num_str)) // error_char points at the end if everything goes as expected..
        {
            return false;
        }
        
        vector_push(vec, num);
        num_str = strtok(NULL, delim);
    }       
    return true;
}