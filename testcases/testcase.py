class Testcase:
    @staticmethod
    def PrintResults(results, print_output = True):
        if not isinstance(results,list):
            results = [results]

        for name, status, output in results:
            print(f"-----Test: {name} ... {'Success' if status else 'Fail'}-----",end="")

            # Output is not to be printed
            if not print_output:
                output = None

            if not output:
                print()
            else:
                print(" Output: ",end="")
                if len(str(output).splitlines()) > 1:
                    print()

                print(output)
            
    @staticmethod
    def RunTests(tests, print_results, return_results, output_level):
        results = []

        for name,test,args in tests:
            result = None
            try:
                output = test(*args)
                result = (name,True,output)
            except Exception as e:
                result = (name,False,e)

            results.append(result)

            # Print the result of the completed test
            if print_results:
                Testcase.PrintResults(result, print_output=True if output_level >= 0 else False)

        # Print a summary of the tests
        if print_results and output_level >= -1:
            passed = len([x for x in results if x[1]])
            failed = len(results) - passed

            print(f"Tests passed: {passed}. Tests failed: {failed}")
        
        if return_results:
            return results
