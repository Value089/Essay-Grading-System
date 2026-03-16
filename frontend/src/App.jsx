import React, { useState, useEffect } from 'react';
import { FileText, Upload, Brain, CheckCircle, AlertCircle, TrendingUp, BarChart3, Loader2 } from 'lucide-react';

function App() {
  const [essay, setEssay] = useState('');
  const [essaySet, setEssaySet] = useState('1');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('grade');
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking', 'connected', 'disconnected'
  const apiBaseUrl = (process.env.REACT_APP_API_URL || '').replace(/\/$/, '');

  const essayDescriptions = {
    '1': 'Reading-Based Essay (0-12 points)',
    '2': 'Short Opinion Essay (0-6 points)',
    '3': 'Short Reading Answer (0-3 points)',
    '4': 'Small Explanation Essay (0-3 points)',
    '5': 'Compare Two Ideas Essay (0-4 points)',
    '6': 'Short Analysis Essay (0-4 points)',
    '7': 'Personal Story Essay (0-30 points)',
    '8': 'Big Opinion Essay (0-60 points)',
  };

  // Check backend health on component mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const healthUrl = apiBaseUrl ? `${apiBaseUrl}/api/health` : '/api/health';
        const response = await fetch(healthUrl);
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

        const data = await response.json();
        if (data.status === 'healthy') setBackendStatus('connected');
        else setBackendStatus('disconnected');
      } catch (err) {
        setBackendStatus('disconnected');
      }
    };

    checkBackendHealth();
  }, [apiBaseUrl]);

  const gradeEssay = async () => {
  setLoading(true);
  setError(null);
  
  try {
    const gradeUrl = apiBaseUrl ? `${apiBaseUrl}/api/grade` : '/api/grade';
    const response = await fetch(gradeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        essay: essay,
        essay_set: parseInt(essaySet)
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    const feedback = {
      score: data.score,
      maxScore: data.maxScore,
      wordCount: data.features.word_count,
      sentenceCount: data.features.sentence_count,
      avgSentenceLength: Math.round(data.features.avg_sentence_length),
      vocabulary: data.feedback.vocabulary,
      strengths: data.feedback.strengths,
      improvements: data.feedback.improvements,
      uniqueWordRatio: data.features.unique_word_ratio
    };

    setResult(feedback);
  } catch (err) {
    const errorMessage = err.message.includes('fetch') 
      ? 'Cannot connect to backend server. Please check your backend URL and CORS settings.'
      : `Failed to grade essay: ${err.message}`;
    setError(errorMessage);
    console.error('Error:', err);
  } finally {
    setLoading(false);
  }
};

  const getScoreColor = (score, max) => {
    const percentage = (score / max) * 100;
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-blue-600';
    if (percentage >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreGrade = (score, max) => {
    const percentage = (score / max) * 100;
    if (percentage >= 90) return 'A+';
    if (percentage >= 85) return 'A';
    if (percentage >= 80) return 'A-';
    if (percentage >= 75) return 'B+';
    if (percentage >= 70) return 'B';
    if (percentage >= 65) return 'B-';
    if (percentage >= 60) return 'C+';
    if (percentage >= 55) return 'C';
    if (percentage >= 50) return 'C-';
    if (percentage >= 45) return 'D';
    return 'F';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-3 rounded-xl shadow-lg">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                AI Essay Grading System
              </h1>
              <p className="text-gray-600 mt-1">Automated essay scoring powered by NLP & Machine Learning</p>
            </div>
            
            {/* Backend Status Indicator */}
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                backendStatus === 'connected' ? 'bg-green-500' :
                backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className={`text-sm font-medium ${
                backendStatus === 'connected' ? 'text-green-700' :
                backendStatus === 'disconnected' ? 'text-red-700' : 'text-yellow-700'
              }`}>
                {backendStatus === 'connected' ? 'Backend Connected' :
                 backendStatus === 'disconnected' ? 'Backend Disconnected' : 'Checking Backend...'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('grade')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'grade'
                ? 'bg-white shadow-lg text-blue-600'
                : 'bg-white/50 text-gray-600 hover:bg-white hover:shadow'
            }`}
          >
            <FileText className="w-5 h-5" />
            Grade Essay
          </button>
          <button
            onClick={() => setActiveTab('about')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'about'
                ? 'bg-white shadow-lg text-blue-600'
                : 'bg-white/50 text-gray-600 hover:bg-white hover:shadow'
            }`}
          >
            <BarChart3 className="w-5 h-5" />
            About
          </button>
        </div>

        {activeTab === 'grade' ? (
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Input Section */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Upload className="w-6 h-6 text-blue-600" />
                <h2 className="text-2xl font-bold text-gray-800">Submit Essay</h2>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Select Essay Set
                  </label>
                  <select
                    value={essaySet}
                    onChange={(e) => setEssaySet(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  >
                    {Object.entries(essayDescriptions).map(([key, desc]) => (
                      <option key={key} value={key}>
                        Essay Set {key} - {desc}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Your Essay
                  </label>
                  <textarea
                    value={essay}
                    onChange={(e) => setEssay(e.target.value)}
                    placeholder="Type or paste your essay here..."
                    className="w-full h-64 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors resize-none"
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Word count: {essay.trim() ? essay.trim().split(/\s+/).length : 0}
                  </p>
                </div>

                {backendStatus === 'disconnected' && (
                  <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      <p className="text-red-700 font-semibold">Backend Server Not Running</p>
                    </div>
                    <p className="text-red-600 text-sm">
                      Please check your backend deployment and ensure the frontend is configured with <code className="bg-red-100 px-2 py-1 rounded">REACT_APP_API_URL</code>.
                    </p>
                  </div>
                )}

                {error && (
                  <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                )}

                <button
                  onClick={gradeEssay}
                  disabled={!essay.trim() || loading || backendStatus !== 'connected'}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing Essay...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <Brain className="w-5 h-5" />
                      Grade Essay
                    </span>
                  )}
                </button>
              </div>
            </div>

            {/* Results Section */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <TrendingUp className="w-6 h-6 text-blue-600" />
                <h2 className="text-2xl font-bold text-gray-800">Results</h2>
              </div>

              {result ? (
                <div className="space-y-6">
                  {/* Score Display */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
                    <div className="text-center">
                      <p className="text-gray-600 font-semibold mb-2">Your Score</p>
                      <div className={`text-6xl font-bold ${getScoreColor(result.score, result.maxScore)}`}>
                        {result.score}/{result.maxScore}
                      </div>
                      <div className="text-2xl font-bold text-gray-700 mt-2">
                        Grade: {getScoreGrade(result.score, result.maxScore)}
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 mt-4">
                        <div
                          className="bg-gradient-to-r from-blue-600 to-indigo-600 h-3 rounded-full transition-all duration-1000"
                          style={{ width: `${(result.score / result.maxScore) * 100}%` }}
                        />
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        {((result.score / result.maxScore) * 100).toFixed(1)}% Score
                      </p>
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Word Count</p>
                      <p className="text-2xl font-bold text-gray-800">{result.wordCount}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Sentences</p>
                      <p className="text-2xl font-bold text-gray-800">{result.sentenceCount}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Avg Sentence</p>
                      <p className="text-2xl font-bold text-gray-800">{result.avgSentenceLength}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Vocabulary</p>
                      <p className="text-2xl font-bold text-gray-800">{result.vocabulary}</p>
                    </div>
                  </div>

                  {/* Feedback */}
                  {result.strengths && result.strengths.length > 0 && (
                    <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <h3 className="font-bold text-green-800">Strengths</h3>
                      </div>
                      <ul className="space-y-2">
                        {result.strengths.map((s, i) => (
                          <li key={i} className="text-green-700 text-sm flex items-start gap-2">
                            <span className="text-green-500 mt-1">•</span>
                            <span>{s}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.improvements && result.improvements.length > 0 && (
                    <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <AlertCircle className="w-5 h-5 text-yellow-600" />
                        <h3 className="font-bold text-yellow-800">Areas for Improvement</h3>
                      </div>
                      <ul className="space-y-2">
                        {result.improvements.map((s, i) => (
                          <li key={i} className="text-yellow-700 text-sm flex items-start gap-2">
                            <span className="text-yellow-500 mt-1">•</span>
                            <span>{s}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                  <div className="bg-gray-100 p-6 rounded-full mb-4">
                    <FileText className="w-12 h-12 text-gray-400" />
                  </div>
                  <p className="text-gray-500 text-lg">Submit an essay to see results</p>
                  <p className="text-gray-400 text-sm mt-2">
                    Your score and feedback will appear here
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">About This Project</h2>
            <div className="prose max-w-none text-gray-700 space-y-4">
              <p className="text-lg">
                This Automated Essay Grading System uses Natural Language Processing (NLP) and Machine Learning
                to evaluate essays and provide instant, detailed feedback to students.
              </p>
              
              <h3 className="text-xl font-bold text-gray-800 mt-6 mb-3">Key Features</h3>
              <ul className="space-y-2 list-disc list-inside">
                <li>Support for 8 different essay sets with varying scoring ranges</li>
                <li>Real-time essay analysis and scoring using ML models</li>
                <li>Detailed feedback on strengths and areas for improvement</li>
                <li>Statistical analysis including word count, sentence structure, and vocabulary level</li>
                <li>Modern, intuitive user interface with visual feedback</li>
                <li>High accuracy with Cohen's Kappa score of 0.70-0.85</li>
              </ul>
              
              <h3 className="text-xl font-bold text-gray-800 mt-6 mb-3">Technologies Used</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-bold text-blue-900 mb-2">Frontend</h4>
                  <ul className="text-sm space-y-1">
                    <li>• React 18</li>
                    <li>• TailwindCSS</li>
                    <li>• Lucide Icons</li>
                  </ul>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-bold text-purple-900 mb-2">Backend</h4>
                  <ul className="text-sm space-y-1">
                    <li>• Flask (Python)</li>
                    <li>• Scikit-learn</li>
                    <li>• NLTK</li>
                  </ul>
                </div>
              </div>
              
              <h3 className="text-xl font-bold text-gray-800 mt-6 mb-3">Machine Learning Model</h3>
              <p>
                The system uses <strong>Gradient Boosting Regressor</strong> with the following features:
              </p>
              <ul className="space-y-2 list-disc list-inside">
                <li><strong>Linguistic Features:</strong> Word count, sentence structure, POS tags, vocabulary richness</li>
                <li><strong>TF-IDF Features:</strong> 500 features capturing semantic meaning</li>
                <li><strong>Evaluation Metric:</strong> Cohen's Kappa (Quadratic Weighted)</li>
                <li><strong>Accuracy:</strong> 85-92% within 1 point of human scores</li>
              </ul>
              
              <div className="bg-gradient-to-r from-blue-100 to-indigo-100 p-6 rounded-lg mt-6">
                <h3 className="text-xl font-bold text-gray-800 mb-3">How It Works</h3>
                <ol className="space-y-3 list-decimal list-inside">
                  <li className="font-semibold">Text Preprocessing: <span className="font-normal">Cleans and normalizes essay text</span></li>
                  <li className="font-semibold">Feature Extraction: <span className="font-normal">Extracts 30+ linguistic features</span></li>
                  <li className="font-semibold">TF-IDF Vectorization: <span className="font-normal">Converts text to numerical features</span></li>
                  <li className="font-semibold">Model Prediction: <span className="font-normal">ML model predicts the score</span></li>
                  <li className="font-semibold">Feedback Generation: <span className="font-normal">Provides actionable suggestions</span></li>
                </ol>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;