export const MARKDOWN_COMPONENTS = {
  h1: ({node, ...props}: any) => <h1 className="text-3xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-blue-300" {...props} />,
  h2: ({node, ...props}: any) => <h2 className="text-2xl font-bold text-gray-800 mt-6 mb-3 pb-2 border-b border-gray-300" {...props} />,
  h3: ({node, ...props}: any) => <h3 className="text-xl font-semibold text-gray-800 mt-4 mb-2" {...props} />,
  h4: ({node, ...props}: any) => <h4 className="text-lg font-semibold text-gray-700 mt-3 mb-2" {...props} />,
  p: ({node, ...props}: any) => <p className="text-gray-700 text-base leading-relaxed mb-4" {...props} />,
  ul: ({node, ...props}: any) => <ul className="space-y-2 my-4 ml-6 list-disc marker:text-blue-600" {...props} />,
  ol: ({node, ...props}: any) => <ol className="space-y-2 my-4 ml-6 list-decimal marker:text-blue-600" {...props} />,
  li: ({node, children, ...props}: any) => {
    const text = children?.toString() || '';
    const startsWithEmoji = text.length > 0 && text.charCodeAt(0) > 127;
    return <li className={`text-gray-700 leading-relaxed pl-2 ${startsWithEmoji ? 'list-none -ml-6' : ''}`} {...props}>{children}</li>;
  },
  strong: ({node, ...props}: any) => <strong className="font-bold text-gray-900" {...props} />,
  em: ({node, ...props}: any) => <em className="italic text-gray-800" {...props} />,
};
