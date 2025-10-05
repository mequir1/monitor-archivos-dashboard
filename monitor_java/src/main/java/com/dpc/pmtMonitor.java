package com.dpc;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.*;

import static java.nio.file.StandardWatchEventKinds.*;

public class pmtMonitor {
    public static void main(String[] args) throws Exception {
        Map<String, String> env = cargarEnv(".env");
        String carpeta = env.get("CARPETA");
        String endpoint = env.get("PYTHON_ENDPOINT");
        String logPath = env.get("LOG_PATH");

        Logger logger = Logger.getLogger("MonitorLogger");
        FileHandler fh = new FileHandler(logPath, true);
        fh.setFormatter(new SimpleFormatter());
        logger.addHandler(fh);

        WatchService watcher = FileSystems.getDefault().newWatchService();
        Path path = Paths.get(carpeta);
        path.register(watcher, ENTRY_CREATE, ENTRY_MODIFY);

        logger.info("👀 Monitoreando carpeta PMT: " + carpeta);

        while (true) {
            WatchKey key = watcher.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                Path archivo = (Path) event.context();
                File file = new File(carpeta + archivo.getFileName());

                if (file.exists() && archivo.getFileName().toString().endsWith(".PMT") && archivo.getFileName().toString().startsWith("Suc")) {    
                    BasicFileAttributes attrs = Files.readAttributes(file.toPath(), BasicFileAttributes.class);
                    long size_bytes = attrs.size();
                    Timestamp modification_date = new Timestamp(attrs.lastModifiedTime().toMillis());

                    String nombreArchivo = archivo.getFileName().toString();
                    String[] partes = nombreArchivo.split("_"); // ["Suc5564", "20250928.PMT"]
                    String sucursal = partes[0].substring(3); // "5564"

                    Integer store_nbr = 0;

                    // Convertir a entero
                    try {
                        int storeNumber = Integer.parseInt(sucursal);
                        System.out.println("Entero convertido: " + storeNumber); // Salida: Entero convertido: 123
                        store_nbr = storeNumber;
                    } catch (NumberFormatException e) {
                        System.err.println("Error al convertir a entero: " + e.getMessage());
                    }

                    pmtReporta(endpoint, archivo.getFileName().toString(), modification_date.toString(), size_bytes, store_nbr, logger);
                }
            }
            key.reset();
        }
    }

    private static Map<String, String> cargarEnv(String ruta) throws IOException {
        Map<String, String> env = new HashMap<>();
        BufferedReader reader = new BufferedReader(new FileReader(ruta));
        String linea;
        while ((linea = reader.readLine()) != null) {
            if (linea.contains("=")) {
                String[] partes = linea.split("=", 2);
                env.put(partes[0].trim(), partes[1].trim());
            }
        }
        reader.close();
        return env;
    }

    private static void pmtReporta(String endpoint, String name_pmt, String modification_date, long size_bytes, Integer store_nbr, Logger logger) {
        try {
            URL url = new URL(endpoint);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json");
            con.setDoOutput(true);

            //int storeNbr = Integer.parseInt(store_nbr);
            String json = String.format("[{\"name_pmt\":\"%s\",\"modification_date\":\"%s\",\"size_bytes\":%d,\"store_nbr\":%d}]", name_pmt, modification_date, size_bytes, store_nbr);

            OutputStream os = con.getOutputStream();
            os.write(json.getBytes());
            os.close();

            int status = con.getResponseCode();
            logger.info("📤 Cadena " + json);
            logger.info("sitio: " + endpoint);
            logger.info("📤 Enviado a Python: " + name_pmt + " → " + status);
            
        } catch (Exception e) {
            logger.severe("❌ Error al enviar a Python: " + e.getMessage());
        }
    }
}
