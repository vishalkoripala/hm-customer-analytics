import java.io.*;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.util.ReflectionUtils;
import org.apache.hadoop.io.SequenceFile;
import org.apache.mahout.clustering.classify.WeightedPropertyVectorWritable;
import org.apache.mahout.math.Vector;

public class ExtractClusters {
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Path input = new Path(args[0]);
        FileSystem fs = input.getFileSystem(conf);

        try (BufferedWriter out = new BufferedWriter(
                new FileWriter(args[1]))) {

            FileStatus[] files = fs.listStatus(input);

            for (FileStatus file : files) {
                if (!file.isFile() ||
                    !file.getPath().getName().startsWith("part-")) {
                    continue;
                }

                try (SequenceFile.Reader reader =
                    new SequenceFile.Reader(
                        conf,
                        SequenceFile.Reader.file(file.getPath()))) {

                    IntWritable key = new IntWritable();
                    WeightedPropertyVectorWritable value =
                        new WeightedPropertyVectorWritable();

                    while (reader.next(key, value)) {
                        Vector v = value.getVector();

                        out.write(key.get() + "\t"
                            + Double.toString(v.get(0)) + "\t"
                            + Double.toString(v.get(1)) + "\t"
                            + Double.toString(v.get(2)));
                        out.newLine();
                    }
                }
            }
        }

        System.out.println("Extraction completed.");
    }
}
