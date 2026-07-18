import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { TopicInput } from './TopicInput';
import { LearningStyleSelect } from './LearningStyleSelect';
import { DifficultySelect } from './DifficultySelect';
import { BloomLevelSelect } from './BloomLevelSelect';
import { InstructionInput } from './InstructionInput';
import { GenerateButton } from './GenerateButton';

export const PromptForm: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [topic, setTopic] = useState(location.state?.topic || '');
  const [learningStyle, setLearningStyle] = useState('');

  const [difficulty, setDifficulty] = useState('');
  const [bloomLevel, setBloomLevel] = useState('');
  const [instructions, setInstructions] = useState('');

  const isFormValid = topic.trim() !== '' && learningStyle !== '' && difficulty !== '' && bloomLevel !== '';

  const handleGenerate = () => {
    if (!isFormValid) return;
    
    const formData = {
      topic,
      learningStyle,
      difficulty,
      bloomLevel,
      instructions
    };
    

    navigate('/loading', { state: { formData } });
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 md:p-8 flex flex-col gap-8">
      <TopicInput value={topic} onChange={setTopic} />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <LearningStyleSelect value={learningStyle} onChange={setLearningStyle} />
        <DifficultySelect value={difficulty} onChange={setDifficulty} />
      </div>

      <BloomLevelSelect value={bloomLevel} onChange={setBloomLevel} />
      
      <InstructionInput value={instructions} onChange={setInstructions} />
      
      <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
        <GenerateButton onClick={handleGenerate} disabled={!isFormValid} />
      </div>
    </div>
  );
};
