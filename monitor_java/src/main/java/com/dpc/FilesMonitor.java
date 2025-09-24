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

public class FilesMonitor {
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

        logger.info("👀 Monitoreando carpeta: " + carpeta);

        while (true) {
            WatchKey key = watcher.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                Path archivo = (Path) event.context();
                File file = new File(carpeta + archivo.getFileName());

                if (file.exists()) {
                    BasicFileAttributes attrs = Files.readAttributes(file.toPath(), BasicFileAttributes.class);
                    long tamaño = attrs.size();
                    Timestamp fecha = new Timestamp(attrs.lastModifiedTime().toMillis());

                    enviarReporte(endpoint, archivo.getFileName().toString(), fecha.toString(), tamaño, logger);
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

    private static void enviarReporte(String endpoint, String nombre, String fecha, long tamaño, Logger logger) {
        try {
            URL url = new URL(endpoint);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json");
            con.setDoOutput(true);

            String json = String.format("{\"nombre\":\"%s\",\"fecha\":\"%s\",\"tamaño\":%d}", nombre, fecha, tamaño);
            OutputStream os = con.getOutputStream();
            os.write(json.getBytes());
            os.close();

            int status = con.getResponseCode();
            logger.info("📤 Enviado a Python: " + nombre + " → " + status);
        } catch (Exception e) {
            logger.severe("❌ Error al enviar a Python: " + e.getMessage());
        }
    }
}
