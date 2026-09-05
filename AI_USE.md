# AI Use Statement

This document describes how AI tools were used during the development of the IncuBrix Video Editor (Video Router) project.

AI assistance was used to improve productivity and support learning. All code, design decisions, tests, experiments, and final results were reviewed and validated by me.

## 1\. AI Tools Used

* OpenAI ChatGPT (GPT-5.6 Luna) through the ChatGPT web interface

## 2\. Areas Where AI Helped

AI assistance was used for:

* Understanding technical concepts and exploring implementation approaches
* Generating and refining code snippets
* Explaining errors and suggesting fixes
* Improving code structure, readability, and organization
* Designing test cases and interpreting test results
* Supporting documentation writing
* Researching open/open-weight video generation models
* Comparing model capabilities, licensing, hardware requirements, and reported performance
* Structuring the routing and fallback logic
* Reviewing the project architecture and implementation

## 3\. My Contribution and Validation

I personally:

* Designed the overall project architecture and workflow
* Implemented and integrated the project code
* Developed the planning, routing, fallback, validation, assembly, logging, and evaluation components
* Ran the complete automated test suite
* Ran the benchmark evaluation and verified the results
* Executed the LTX-Video model on approved free Google Colab T4 compute
* Recorded the actual LTX-Video generation measurements
* Verified model capabilities and licensing information using official sources
* Tested FFmpeg-based video assembly, captions, timeline generation, and validation
* Created and tested the three workflow variants: education, news, and product
* Reviewed and modified AI-suggested code before integrating it
* Ensured that the final implementation and reported measurements reflect my own understanding and validation

## 4\. Use of AI-Generated Code

AI-generated code was not used blindly.

Code suggestions were reviewed, modified where necessary, integrated into the repository, and tested against the project's requirements. I made implementation decisions and verified that the resulting code worked correctly.

The final repository contains code that I understand, tested, and modified as required for the project.

## 5\. Experimental Results

AI assistance was used to help plan and troubleshoot experiments, but experimental results were obtained from actual execution.

In particular, the LTX-Video baseline was executed on an approved free Google Colab T4 environment. The successful run used the LTX-Video 2B distilled checkpoint with a measured runtime of approximately 19 seconds for the tested configuration.

The measured result was not treated as an AI-generated estimate.

## 6\. Limitations

AI tools can provide incomplete or incorrect information.

Critical technical information, including model capabilities, licensing, hardware requirements, and reported performance, was checked against official model sources where applicable.

Measured performance claims were based on actual project experiments rather than unverified AI estimates.

## 7\. Conclusion

AI assistance was used as a learning, development, debugging, and productivity tool.

The final project, including its implementation, tests, experimental results, documentation, and engineering decisions, was reviewed and validated by me. AI assistance supported the development process but did not replace my responsibility for the final implementation or results.

