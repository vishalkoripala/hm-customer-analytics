import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.SequenceFile;
import org.apache.mahout.clustering.classify.WeightedPropertyVectorWritable;
import org.apache.mahout.math.Vector;

public class ExtractClusters {

    public static void main(String[] args) throws IOException {

        if (args.length != 2) {
            System.err.println(
                "Usage: ExtractClusters <input-directory> <output-file>"
            );
            System.exit(1);
        }

        Configuration conf = new Configuration();

        Path input = new Path(args[0]);
        Path output = new Path(args[1]);

        FileSystem fs = input.getFileSystem(conf);

        if (!fs.exists(input) || !fs.getFileStatus(input).isDirectory()) {
            throw new IOException(
                "Input path does not exist or is not a directory: " + input
            );
        }

        FileStatus[] files = fs.listStatus(input);

        int filesProcessed = 0;
        long recordsExtracted = 0;

        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(
                    fs.create(output, true),
                    StandardCharsets.UTF_8
                ))) {

            for (FileStatus file : files) {

                if (!file.isFile()
                        || !file.getPath().getName().startsWith("part-")) {
                    continue;
                }

                try (SequenceFile.Reader reader =
                        new SequenceFile.Reader(
                            conf,
                            SequenceFile.Reader.file(file.getPath())
                        )) {

                    IntWritable key = new IntWritable();

                    WeightedPropertyVectorWritable value =
                        new WeightedPropertyVectorWritable();

                    while (reader.next(key, value)) {

                        Vector vector = value.getVector();

                        if (vector.size() < 3) {
                            throw new IOException(
                                "Invalid vector in " + file.getPath()
                                + ": expected at least 3 features."
                            );
                        }

                        writer.write(
                            key.get() + "\t"
                            + Double.toString(vector.get(0)) + "\t"
                            + Double.toString(vector.get(1)) + "\t"
                            + Double.toString(vector.get(2))
                        );

                        writer.newLine();
                        recordsExtracted++;
                    }
                }

                filesProcessed++;
            }
        }

        if (filesProcessed == 0) {
            throw new IOException(
                "No valid part-* SequenceFiles found in: " + input
            );
        }

        System.out.println("Extraction completed successfully.");
        System.out.println("Part files processed: " + filesProcessed);
        System.out.println("Cluster records extracted: " + recordsExtracted);
        System.out.println("Output file: " + output);
    }
}
