from .testcase import Testcase
class PLCTest (Testcase):
    PLCConnection = None

    def __TestImport():
        import control
        PLCTest.PLCConnection = control.PLCConnection
        return None

    def __TestConnection(ip_address=None, port=None):
        function_args = {}
        for item in [("ip_address",ip_address),("port_number",port)]:
            name, val = item
            if val is not None:
                function_args |= {name: val}
        client = PLCTest.PLCConnection(**function_args)
        return client.connectToPlc()

    def Test(ip_address=None, port=None, print_results=False, return_results=True, output_level=0):

        tests = [
                 ("Importing PLCClient",PLCTest.__TestImport,[]),
                 ("Connect to PLC",PLCTest.__TestConnection,[ip_address,port])
                 ]

        return Testcase.RunTests(tests,print_results,return_results,output_level)



if __name__ == "__main__":
    results = PLCTest.Test(print_results=True)
