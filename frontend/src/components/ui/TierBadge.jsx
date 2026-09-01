import React from 'react';

export const TierBadge = ({ tier }) => {
  const styles = {
    Blockbuster: 'bg-[#ffb829]/15 text-[#ffb829] border-[#ffb829]/30',
    Hit: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    'Break-even': 'bg-[#8052ff]/15 text-[#8052ff] border-[#8052ff]/30',
    Flop: 'bg-[#ff5c7a]/15 text-[#ff5c7a] border-[#ff5c7a]/30',
  };

  const currentStyle = styles[tier] || 'bg-zinc-800 text-zinc-300 border-zinc-700';

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${currentStyle}`}>
      {tier || 'Unknown'}
    </span>
  );
};
