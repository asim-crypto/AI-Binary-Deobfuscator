// ghidra_scripts/ApplyLabels.java
import java.io.FileReader;
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Variable;
import ghidra.program.model.symbol.SourceType;

public class ApplyLabels extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("[*] Starting AI Label Reintegration...");

        String jsonPath = System.getProperty("user.dir") + "/ai_annotations.json";
        
        JsonParser parser = new JsonParser();
        JsonElement rootElement = parser.parse(new FileReader(jsonPath));
        if (!rootElement.isJsonObject()) {
            printerr("[-] Annotations file root is not a valid JSON object.");
            return;
        }

        JsonObject annotations = rootElement.getAsJsonObject();
        int tx = currentProgram.startTransaction("Apply AI Annotations");
        boolean commit = false;

        try {
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            int updatedCount = 0;

            for (Function function : functions) {
                String originalName = function.getName();
                if (!annotations.has(originalName)) {
                    continue;
                }

                JsonObject data = annotations.getAsJsonObject(originalName);

                // 1. Rename Function
                if (data.has("suggested_function_name")) {
                    String newName = data.get("suggested_function_name").getAsString();
                    if (!newName.isEmpty() && !newName.equals(originalName)) {
                        function.setName(newName, SourceType.USER_DEFINED);
                        println("[+] Renamed function: " + originalName + " -> " + newName);
                    }
                }

                // 2. Set Function Summary as Plate Comment
                if (data.has("purpose")) {
                    String purpose = data.get("purpose").getAsString();
                    function.setComment(purpose);
                    println("    [+] Added purpose comment to: " + function.getName());
                }

                // 3. Rename Local Variables
                if (data.has("variable_renames") && data.get("variable_renames").isJsonObject()) {
                    JsonObject varRenames = data.getAsJsonObject("variable_renames");
                    for (Variable var : function.getAllVariables()) {
                        String oldVarName = var.getName();
                        if (varRenames.has(oldVarName)) {
                            String newVarName = varRenames.get(oldVarName).getAsString();
                            var.setName(newVarName, SourceType.USER_DEFINED);
                            println("    [+] Renamed variable: " + oldVarName + " -> " + newVarName);
                        }
                    }
                }
                updatedCount++;
            }

            commit = true;
            println("[+] Completed reintegration. Updated " + updatedCount + " functions.");
        } catch (Exception e) {
            printerr("[-] Reintegration error: " + e.getMessage());
        } finally {
            currentProgram.endTransaction(tx, commit);
        }
    }
}
