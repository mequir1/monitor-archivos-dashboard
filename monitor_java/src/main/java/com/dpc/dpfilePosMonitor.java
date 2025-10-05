package com.dpc;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.URL;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.sql.Timestamp;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.*;
//import java.net.InetAddress;
//import java.net.NetworkInterface;
//import java.net.Inet4Address;


import static java.nio.file.StandardWatchEventKinds.*;

public class dpfilePosMonitor {
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

        logger.info("👀 Monitoreando carpeta DPFILES: " + carpeta);

        while (true) {
            WatchKey key = watcher.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                Path archivo = (Path) event.context();
                File file = new File(carpeta + archivo.getFileName());


                if (file.exists() && archivo.getFileName().toString().endsWith("DPFILE")) {    
                    BasicFileAttributes attrs = Files.readAttributes(file.toPath(), BasicFileAttributes.class);
                    long size_bytes = attrs.size();
                    Timestamp modification_date = new Timestamp(attrs.lastModifiedTime().toMillis());

                    Integer store_nbr = 0; // Valor por default sino puede covertir Suc
                    String pos_nbr = "0";
                    pmtReporta(endpoint, store_nbr, pos_nbr, modification_date.toString(), size_bytes, logger);
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

    private static void pmtReporta(String endpoint, Integer store_nbr, String pos_nbr, String modification_date, long size_bytes, Logger logger) {
        try {
            URL url = new URL(endpoint);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json");
            con.setDoOutput(true);

            //int storeNbr = Integer.parseInt(store_nbr);
            String ip_nbr = obtenerIP();
            String hostname = obtenerHostname();

            String json = String.format("[{\"store_nbr\":%d,\"pos_nbr\":\"%s\",\"ip_nbr\":\"%s\",\"modification_date\":\"%s\",\"size_bytes\":%d}]", store_nbr, pos_nbr, ip_nbr ,modification_date, size_bytes);
            OutputStream os = con.getOutputStream();
            os.write(json.getBytes());
            os.close();

            int status = con.getResponseCode();
            logger.info("📤 Cadena " + json);
            logger.info("sitio: " + endpoint);
            logger.info("📤 Enviado a Python: " + ip_nbr + " Name: "+ hostname +" → " + status);
            
        } catch (Exception e) {
            logger.severe("❌ Error al enviar a Python: " + e.getMessage());
        }
    }

    private static String obtenerIP() {
        try {
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
            while (interfaces.hasMoreElements()) {
                NetworkInterface ni = interfaces.nextElement();
                Enumeration<InetAddress> addresses = ni.getInetAddresses();
                while (addresses.hasMoreElements()) {
                    InetAddress addr = addresses.nextElement();
                    if (!addr.isLoopbackAddress() && addr instanceof Inet4Address) {
                        return addr.getHostAddress();
                    }
                }
            }
        } catch (Exception e) {
            return "0.0.0.0";
        }
        return "0.0.0.0";
    }

    private static String obtenerHostname() {
        try {
            return InetAddress.getLocalHost().getHostName();
        } catch (Exception e) {
            return "unknown-host";
        }
    }
}
