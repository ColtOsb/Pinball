#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct metric {
  char* name;
  double initial_performance;
  double end_performance;
};

int CreateNewMetric(struct metric** metrics, int* num_metrics, int* max_num_metrics, char* name, double performance){
  // Allocates more memory if needed
  if (*num_metrics > *max_num_metrics){
    struct metric* temp_pointer;
    temp_pointer = reallocarray((*metrics),*num_metrics * 2, sizeof(struct metric));
    // temp_pointer will be not NULL if the realloc was successful.
    if(temp_pointer){
      *metrics = temp_pointer;
      *max_num_metrics = *max_num_metrics * 2;
    } else {
      return 1;
    }
  }

  // Create actual struct
  struct metric new_metric;
  new_metric.name = malloc(strlen(name));
  // Failed to allocate memory for name string
  if (!new_metric.name){
    return 1;
  }
  // Failed to copy string
  if(!strcpy(new_metric.name,name)){
    return 1;
  }
  new_metric.initial_performance = performance;
  (*metrics)[*num_metrics] = new_metric;
  (*num_metrics)++;
  return 0;
}

int UpdateMetric(struct metric** metrics, int* num_metrics, int* max_num_metrics, char* name, double performance){
  if(*num_metrics <= 0){
    return 1;
  }
  for(int i = 0; i < *num_metrics && (*metrics)[i].name != NULL; ++i){
    if (!strcmp((*metrics)[i].name,name)){
      printf("Exists\n");
      (*metrics)[i].end_performance = performance;
      return 0;
    }
  }
  return CreateNewMetric(metrics,num_metrics,max_num_metrics,name,performance);
}

int ReadFile(struct metric** metrics, int* num_metrics, int* max_num_metrics, FILE* file){ 
  int buffer_size = 256;
  char buffer[buffer_size];
  char* colon = NULL;
  char* name_start = NULL;
  int name_length = 0;
  while(fgets(buffer,buffer_size,file)){
    
    if((colon = strchr(buffer,':')) && colon > buffer){
      int i;
      for(i = colon-buffer; i > 1 && buffer[i-1] != ' '; --i ){
        ; // Loop continues until start of buffer or space was found
      }
      name_start = &(buffer[i]);
      name_length = colon - name_start;
      name_start[name_length-1] = '\0';
      printf("length: %d - %s ~",name_length,name_start);

      // Start looking for time
      if(colon - buffer > 0){
        if((colon = strchr(colon+1,':')) && colon < buffer+buffer_size-2){
          double time = strtod(colon+1,NULL);
          printf("%s ~",colon);
          printf("%f\n",time);
          
          if(UpdateMetric(metrics,num_metrics,max_num_metrics,name_start,time)){
            perror("Create new metric.");
          }
        }
      }
    }
  }
  return 0;
}

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

  int max_num_metrics = 10;
  int num_metrics = 0;
  struct metric* metrics = malloc(sizeof(struct metric) * max_num_metrics);
  if (!metrics){
    perror("Allocate metrics.");
    exit(1);
  }
  ReadFile(&metrics,&num_metrics,&max_num_metrics,initial);
  ReadFile(&metrics,&num_metrics,&max_num_metrics,end);
  
  return 0;
}
