export default function About() {
  return (
    <div className="max-w-3xl">
      <h2 className="text-2xl font-bold mb-6">About / How It Works</h2>
      <p className="mb-4">
        This project uses Apache Spark and Spark MLlib to train a logistic regression model on anonymized credit card transactions.
      </p>
      <div className="bg-[#191919] rounded shadow p-4 mb-4">
        <h3 className="font-semibold mb-2">Architecture flow</h3>
        <p>Dataset ? FastAPI backend ? Spark MLlib pipeline ? predictions and metrics ? local storage or AWS S3.</p>
        <p className="mt-2">EC2 runs the application and computation; S3 stores input data and results.</p>
      </div>
      <div className="bg-[#191919] rounded shadow p-4">
        <h3 className="font-semibold mb-2">Glossary</h3>
        <ul className="list-disc pl-5 space-y-1 text-sm">
          <li><strong>Fraud</strong>: a transaction predicted as potentially fraudulent.</li>
          <li><strong>Prediction probability</strong>: model estimate, not a guaranteed real-world fraud probability.</li>
          <li><strong>Precision</strong>: of predicted frauds, how many were actually fraud.</li>
          <li><strong>Recall</strong>: of actual frauds, how many were detected.</li>
          <li><strong>F1-score</strong>: balance between precision and recall.</li>
          <li><strong>ROC-AUC</strong>: how well the model separates fraud from legitimate transactions.</li>
        </ul>
      </div>
    </div>
  )
}
