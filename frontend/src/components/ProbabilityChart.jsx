import React from 'react';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const COLORS = { '<30': '#287b58', '>30': '#d39b42', NO: '#859c92' };
const NAMES = { '<30': 'Within 30 days', '>30': 'After 30 days', NO: 'Not readmitted' };

export default function ProbabilityChart({ result }) {
  const data = [
    { code: '<30', name: NAMES['<30'], probability: result.probability_lt30 * 100 },
    { code: '>30', name: NAMES['>30'], probability: result.probability_gt30 * 100 },
    { code: 'NO', name: NAMES.NO, probability: result.probability_no * 100 },
  ];
  return <div className="probability-chart" aria-label="Probability distribution for all three outcomes">
    <ResponsiveContainer width="100%" height={146}>
      <BarChart data={data} layout="vertical" margin={{ top: 1, right: 25, bottom: 0, left: 5 }} barSize={17}>
        <CartesianGrid horizontal={false} stroke="#e8eeea" />
        <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fill: '#809087', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="code" width={43} tick={{ fill: '#42574d', fontSize: 12, fontWeight: 700 }} axisLine={false} tickLine={false} />
        <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Probability']} labelFormatter={(label) => NAMES[label]} cursor={{ fill: '#f4f7f5' }} />
        <Bar dataKey="probability" radius={[0, 5, 5, 0]}>
          {data.map((entry) => <Cell key={entry.code} fill={COLORS[entry.code]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
    <div className="probability-legend">{data.map((entry) => <div key={entry.code}><span style={{ background: COLORS[entry.code] }} /><span>{entry.name}</span><strong>{entry.probability.toFixed(1)}%</strong></div>)}</div>
  </div>;
}
