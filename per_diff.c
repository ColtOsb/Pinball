#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct metric {
  char* name;
  int initial_performance;
  int end_performance;
};

int main(int argc, char* argv[]){
  if (argc != 3){
    fprintf(stderr,"Usage: %s, <start_file> <end_file>\n",argv[0]);
    exit(1);
  }

  FILE* initial;
  if(!(initial = fopen(argv[1],"r"))){
    perror("First file argument");
    exit(1);
  }
  FILE* end;
  if(!(end = fopen(argv[2],"r"))){
    perror("Second file argument");
    exit(1);
  }

  int buffer_size = 256;
  char buffer[buffer_size];
  char* colon = NULL;
  char* name_start = NULL;
  int name_length = 0;
  while(fgets(buffer,buffer_size,initial)){
    
    if((colon = strchr(buffer,':')) && colon > buffer){
      int i;
      for(i = colon-buffer; i > 1 && buffer[i-1] != ' '; --i ){
        ; // Loop continues until start of buffer or space was found
      }
      name_start = &(buffer[i]);
      name_length = colon - name_start;
      printf("length: %d - %.*s\n",name_length,name_length,name_start);
    }
  }
  return 0;
}
