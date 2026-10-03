// ghidra_scripts/ExtractFunctions.java
import java.io.FileWriter;
import java.util.HashMap;
import java.util.Map;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class ExtractFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("[*] Starting Headless Extraction (Java)...");

        // 1. Initialize Decompiler
        DecompInterface decompInterface = new DecompInterface();
        decompInterface.openProgram(currentProgram);

        Map<String, String> outputData = new HashMap<>();
        
        // 2. Get all functions
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);

        for (Function function : functions) {
            if (function.isExternal()) {
                continue; // Skip external libraries like printf
            }
            
            // 3. Decompile
            DecompileResults results = decompInterface.decompileFunction(function, 0, monitor);
            if (results != null && results.decompileCompleted()) {
                String cCode = results.getDecompiledFunction().getC();
                outputData.put(function.getName(), cCode);
            }
        }

        // 4. Save to JSON
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        String json = gson.toJson(outputData);

        // Get current working directory (where you run the headless command)
        String outPath = System.getProperty("user.dir") + "/extracted_functions.json";
        
        try (FileWriter file = new FileWriter(outPath)) {
            file.write(json);
            println("[+] Successfully extracted " + outputData.size() + " functions to " + outPath);
        }
    }
}
