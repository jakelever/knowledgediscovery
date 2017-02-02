/**
 * Based on LingPipe AbstractSentenceDemo
 */

import org.xml.sax.SAXException;
import com.aliasi.chunk.Chunk;
import com.aliasi.chunk.Chunking;
import com.aliasi.sentences.SentenceChunker;
import com.aliasi.sentences.SentenceModel;
import com.aliasi.tokenizer.Tokenizer;
import com.aliasi.tokenizer.TokenizerFactory;
import com.aliasi.xml.SAXWriter;
import java.lang.reflect.InvocationTargetException;
import java.util.Iterator;
import java.util.Properties;
import com.aliasi.tokenizer.IndoEuropeanTokenizerFactory;
import com.aliasi.sentences.MedlineSentenceModel;
import java.util.Scanner;

/**
 * Based on the AbstractSentenceDemo, this is a simple sentence splitting
 * bit of code
 */
public class LingpipeSentenceSplitter {

	protected final TokenizerFactory mTokenizerFactory;
	protected final SentenceModel mSentenceModel;
	protected final SentenceChunker mSentenceChunker;

	/**
	 * Construct a sentence demo using the specified tokenizer
	 * factory and model.  The factory and model are reconstituted
	 * using reflection using zero-argument constructors.
	 *
	 * @param tokenizerFactoryClassName Name of tokenizer factory class.
	 * @param sentenceModelClassName Name of sentence model class.
	 * @param demoName Name of the demo.
	 * @param demoDescription Plain text description of the demo.
	 */
	public LingpipeSentenceSplitter() {
		
		mTokenizerFactory = new IndoEuropeanTokenizerFactory();
		mSentenceModel = new MedlineSentenceModel();
		mSentenceChunker = new SentenceChunker(mTokenizerFactory,mSentenceModel);
	}

	/**
	 * Extracts sentences and outputs them
	 *
	 * @param cs Underlying characters.
	 * @param start Index of the first character of slice.
	 * @param end Index of one past the last character of the slice.
	 * @param writer SAXWriter to which output is written.
	 * @param properties Properties for the processing.
	 * @throws SAXException If there is an error during processing.
	 */
	public void process(String text) 
	{
		// Chunk the text into sentences
		Chunking sentenceChunking = mSentenceChunker.chunk(text);
		
		// Then iterate over the chunks and output them
		Iterator<Chunk> sentenceIt = sentenceChunking.chunkSet().iterator();
		for (int i = 0; sentenceIt.hasNext(); ++i) {
			Chunk sentenceChunk = sentenceIt.next();
			int sentStart = sentenceChunk.start();
			int sentEnd = sentenceChunk.end();
			String sentenceText = text.substring(sentStart,sentEnd);
			System.out.println(sentenceText);
		}
		System.out.println("");
	}		

	public static void main(String[] args) {
		LingpipeSentenceSplitter splitter = new LingpipeSentenceSplitter();
		
		// Process every line input from stdIn
		Scanner scanner = new Scanner(System.in);
		while (scanner.hasNext()) {
			splitter.process(scanner.nextLine());
		}
	}

}

