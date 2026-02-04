/**
 * @file perf_diff.c
 * @brief Calculates a difference between metrics across two files. Also computes the total difference.
 * Compile with gcc -Wall perf_diff.c -o perf_diff
 *   Add -D DEBUG=1 at the end to add additional debug information
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Converts two doubles to a percentage
#define percent(a,b) (((a / b) - 1.0) * 100)

// Compile with -D DEBUG=1 (for gcc) to enable extra output
#ifndef DEBUG
#define DEBUG 0
#endif

// Use DEBUG_PRINT(format string, arguments); to print something only when DEBUG is defined
#define DEBUG_PRINT(fmt, ...) do { if (DEBUG) fprintf(stderr, "%s:%d:%s(): " fmt, __FILE__, __LINE__, __func__, __VA_ARGS__); } while (0)


// Stores a metric for the diff, contains the name and start and end times
struct metric {
  char* name;
  double initial_performance;
  double end_performance;
};


/**
 * @brief Creates a new metric structure
 *
 * @param metrics metric** address of array of metric structures
 * @param num_metrics int* for current number of metrics in the array
 * @param max_num_metrics int* for size of array storing metrics. Will be updated if array has to be resized
 * @param name char* name of the metric
 * @param performance double time taken on this metric
 * @return 0 on success, 1 on failure
 */
int CreateNewMetric(struct metric** metrics, int* num_metrics, int* max_num_metrics, char* name, double performance){
  
  // If metrics array is full, allocate more memory for the metric structures
  if (*num_metrics >= *max_num_metrics){
    DEBUG_PRINT("Metric array is full. Current num of metrics: %d, max num of metrics: %d\n",*num_metrics,*max_num_metrics);
    struct metric* temp_pointer;
    temp_pointer = reallocarray((*metrics),*num_metrics * 2, sizeof(struct metric));
    // temp_pointer will be not NULL if the realloc was successful.
    if(temp_pointer){
      *metrics = temp_pointer;
      *max_num_metrics = *max_num_metrics * 2;
      DEBUG_PRINT("Resized metric array to: %d\n",*max_num_metrics);
    } else { // temp_pointer is NULL, so reallocarray was unsuccessful.
      perror("Realloc metric array.");
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

  // Because this is creating a new metric struct, this must be the initial performance
  new_metric.initial_performance = performance;
  (*metrics)[*num_metrics] = new_metric;
  (*num_metrics)++;
  return 0;
}


/**
 * @brief Either updates an existing metric or create a new one if needed.
 *
 * @param metrics metric** address of array of metric structures
 * @param num_metrics int* for current number of metrics in the array
 * @param max_num_metrics int* for size of array storing metrics. Will be updated if array has to be resized
 * @param name char* name of the metric
 * @param performance double time taken on this metric
 * @return 0 on success, 1 on failure
 */
int UpdateMetric(struct metric** metrics, int* num_metrics, int* max_num_metrics, char* name, double performance){
  // Does not do anything if num_metrics is less than 0
  if(*num_metrics < 0){
    return 1;
  }

  // Loops through each metric, trying to find existing one with a name matching
  for(int i = 0; i < *num_metrics && (*metrics)[i].name != NULL; ++i){
    if (!strcmp((*metrics)[i].name,name)){ // Name matches
      DEBUG_PRINT("Metric \'%s\' exists, updating metric's end performance to: %f\n",name,performance);
      // Because there is an existing metric, this performance must be the end file 
      (*metrics)[i].end_performance = performance;
      return 0;
    }
  }
  
  // Existing metric was not found, so create a new one.
  DEBUG_PRINT("Metric \'%s\' does not exist, creating new metric with initial performance: %f\n",name,performance);
  return CreateNewMetric(metrics,num_metrics,max_num_metrics,name,performance);
}


/**
 * @brief Reads through the file and updates/creates metrics for each one contained in the file
 *
 * @param metrics metric** address of array of metric structures
 * @param num_metrics int* for current number of metrics in the array
 * @param max_num_metrics int* for size of array storing metrics. Will be updated if array has to be resized
 * @param file FILE* object for the file to read
 * @return always 0
 */
int ReadFile(struct metric** metrics, int* num_metrics, int* max_num_metrics, FILE* file){ 
  int buffer_size = 256;
  char buffer[buffer_size];
  char* colon = NULL; // Points to colon found on line
  char* name_start = NULL; // Points to start of name of metric
  while(fgets(buffer,buffer_size,file)){
    
    // Finds the first colon in the line, which must be appended to the name of the metric
    if((colon = strchr(buffer,':')) && colon > buffer){
      int i;
      for(i = colon-buffer; i > 1 && buffer[i-1] != ' '; --i ){
        ; // Loop continues until start of buffer or space was found
      }
      name_start = &(buffer[i]);
      colon[0] = '\0'; // Replaces colon with null terminator

      // Prints out the name of the metric
      DEBUG_PRINT("Metric found: \'%s\' of length %d\n",name_start,(int)(colon - name_start));

      // Start looking for time, starting from previous colon
      if(colon - buffer > 0){
        // Searches for colon, starting from character after first colon
        if((colon = strchr(colon+1,':')) && colon < buffer+buffer_size-2){
          colon += 1;
          double time = strtod(colon,NULL); // Converts the str to a double
          // Prints out the double of the cast from the string, then the string
          DEBUG_PRINT("Performance for metric: \'%s\' cast to double: %f <- from string: %s",name_start,time,colon);
          
          // Attempts to update the necessary metric structure, making a new one if needed
          if(UpdateMetric(metrics,num_metrics,max_num_metrics,name_start,time)){
            perror("Update metric."); // Some error occured while updating metrics
          }
        }
      }
    }
  }
  return 0;
}


/**
 * @brief Prints information about a metric
 *
 * @param name char* name of the metric to print
 * @param initial_perf double initial performance of the metric
 * @param end_perf double ending performance of the metric
 */
void PrintMetric(char* name, double initial_perf, double end_perf){
    printf("    %s: %f -> %f (%f%%)\n",name,initial_perf,end_perf,percent(end_perf,initial_perf));
}


/**
 * @brief Prints out the difference in each metric, then the total change per frame.
 *
 * @param metrics Array of metric structures
 * @param num_metrics Number of metrics to in the array (This is how many will be traversed)
 */
void DisplayMetricsDiff(struct metric* metrics,int num_metrics){
  double initial_frame_time = 0; // Running total per frame for initial file
  double end_frame_time = 0; // Running total per frame for end file

  // Prints out each metric individually
  printf("Metrics:\n");
  for(int i = 0; i < num_metrics; ++i){
    // Updates totals
    initial_frame_time += metrics[i].initial_performance;
    end_frame_time += metrics[i].end_performance;

    // Prints out the information for the metric 
    PrintMetric(metrics[i].name,metrics[i].initial_performance,metrics[i].end_performance);
  }

  // Prints out the total stats
  printf("Total:\n");
    PrintMetric("Per Frame:",initial_frame_time, end_frame_time);

}


/**
 * @brief Prints from the current location of the file up to the first encountered newline, including it. May read beyond this newline, which will remove the characters from the buffer.
 *
 * @param file FILE* object to read from
 */
void PrintToNewLine(FILE* file){
  int buffer_size = 256;
  char buffer[buffer_size]; // Stores information read
  char* newline = NULL; // Points to newline character
  while(fgets(buffer,buffer_size,file)){
    if((newline = strchr(buffer,'\n'))){ // Searches string to find '\n'
      newline[0] = '\0'; // Replaces newline character with null terminator so that it can be printed
      printf("%s\n",buffer);
      break;
    }
    printf("%s",buffer);
  }
}


/**
 * @brief Rewinds the files and prints their first line with an arrow between the initial and end files. Display looks like so:  
 * <initial_name>: <first line of initial>
 *     |
 *     v
 * <end_name>: <first line of end>
 *
 * @param initial FILE* object for the initial point of reference file
 * @param end FILE* object for the end point of reference file
 * @param initial_name File name for initial object
 * @param end_name File name for end object
 */
void DisplayRunDescriptions(FILE* initial, FILE* end, char* initial_name, char* end_name){
  // Rewinds to beginning of files
  rewind(initial);
  rewind(end);

  // Prints name of first file, then its first line
  printf("%s: ",initial_name);
  PrintToNewLine(initial);

  // Arrow pointing between initial and end
  printf("    |\n    V\n");

  // Prints name of end file, then its first line
  printf("%s: ",end_name);
  PrintToNewLine(end);
}


/**
 * @brief Prints out the version number of the program
 *
 * @param argv Index 0 must store the name of the executable
 */
void PrintVersion(char* argv[]){
  // Version will be printed as 'major_version.minor_version'
  int major_version = 1;
  int minor_version = 2;

  // Date will be printed as 'day month year'
  char* day = "03";
  char* month = "Februrary";
  char* year = "2026";

  // The list of authors to be printed
  char* authors = "Josh Gillum";
  printf("%s %d.%d (%s %s %s)\n",argv[0],major_version,minor_version,day,month,year);
  printf("Written by %s for the University of Idaho.\n", authors);
}


/**
 * @brief Prints out the help information for the program
 *
 * @param argv Index 0 must store name of executable
 */
void PrintHelp(char* argv[]){
  printf("Usage: %s <start_file> <end_file>\n",argv[0]);
  printf("\nThis program will compare the difference between two files that store performance metrics. The results will be printed out on a per-metric basis. The results will be:\n <name>: <first file perf.> -> <second file perf.> (percent change).");
  printf("\nThe two files storing the performance metrics must adhere to the following format:\n * The first line of each file will store what change the metric represents. Ex: \'Changed sorting algorithm to quick sort\'\n * Each metric must be on a newline. Each metric must have the following form: \n   \'* <name>: * :<time per unit>\'. Note that star can be any text, so long as it does not contain a colon. \n      Ex: \'Total time spent on display: 1.7236438290000013 over 3625 iterations. Average: 0.0004754879528275866\'\n        In this case, the metric's name will be \'display\', and its performance will be \'0.000475...\' \n * Both files must contain the same metrics, with the same names (case sensitive).\n");
}


int main(int argc, char* argv[]){
  // Parses arguments to see if user entered a valid argument
  if(argc == 2){
    // Prints version number
    if((strcmp(argv[1],"--version") == 0) || (strcmp(argv[1],"-v") == 0)){
      PrintVersion(argv);
      return 0;
    }

    // Prints help dialogue
    if((strcmp(argv[1],"--help") == 0) || (strcmp(argv[1],"-h") == 0)){
      PrintHelp(argv);
      return 0;
    }
  } 

  // The other argument combinations were not found, thus 2 arguments on
  // command line is the only option left
  if (argc != 3){
    fprintf(stderr,"Usage: %s <start_file> <end_file>\n",argv[0]);
    exit(1);
  }

  // Opens the first file specified in command line
  FILE* initial;
  if(!(initial = fopen(argv[1],"r"))){
    perror("First file argument");
    exit(1);
  }

  // Opens the second file specified in command line
  FILE* end;
  if(!(end = fopen(argv[2],"r"))){
    perror("Second file argument");
    exit(1);
  }

  int max_num_metrics = 10; // Size of array storing metrics
  int num_metrics = 0; // Current number of metrics stored in array
  struct metric* metrics = malloc(sizeof(struct metric) * max_num_metrics);
  
  // Error occured while trying to allocate memory for metrics array
  if (!metrics){
    perror("Allocate metrics.");
    exit(1);
  }

  // Reads metrics from the two files
  DEBUG_PRINT("Reading file: \'%s\'\n",argv[1]);
  ReadFile(&metrics,&num_metrics,&max_num_metrics,initial);
  DEBUG_PRINT("Reading file: \'%s\'\n",argv[2]);
  ReadFile(&metrics,&num_metrics,&max_num_metrics,end);

  // Prints first line of each file
  DisplayRunDescriptions(initial,end,argv[1],argv[2]);

  // Closes files
  fclose(initial);
  fclose(end);
  printf("\n");

  // Displays each metric, then the total of all the metrics
  DisplayMetricsDiff(metrics,num_metrics);
  
  return 0;
}
