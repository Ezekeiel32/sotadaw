/* ------------------------------------------------------------
name: "fx_deess"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxDeess -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxDeess_H__
#define  __FxDeess_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxDeess
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float FxDeess_faustpower2_f(float value) {
	return value * value;
}

class FxDeess : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	float fVec0[2];
	float fRec1[2];
	float fRec0[3];
	float fConst2;
	FAUSTFLOAT fHslider1;
	float fConst3;
	float fConst4;
	float fRec3[2];
	FAUSTFLOAT fHslider2;
	float fConst5;
	float fRec2[2];
	float fRec5[2];
	float fRec4[3];
	float fVec1[2];
	float fRec7[2];
	float fRec6[3];
	float fRec9[2];
	float fRec8[2];
	float fRec11[2];
	float fRec10[3];
	
 public:
	FxDeess() {}

	void metadata(Meta* m) { 
		m->declare("analyzers.lib/amp_follower_ar:author", "Jonatan Liljedahl, revised by Romain Michon");
		m->declare("analyzers.lib/name", "Faust Analyzer Library");
		m->declare("analyzers.lib/version", "1.2.0");
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxDeess -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("compressors.lib/compression_gain_mono:author", "Julius O. Smith III");
		m->declare("compressors.lib/compression_gain_mono:copyright", "Copyright (C) 2014-2020 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("compressors.lib/compression_gain_mono:license", "MIT-style STK-4.3 license");
		m->declare("compressors.lib/compressor_lad_mono:author", "Julius O. Smith III");
		m->declare("compressors.lib/compressor_lad_mono:copyright", "Copyright (C) 2014-2020 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("compressors.lib/compressor_lad_mono:license", "MIT-style STK-4.3 license");
		m->declare("compressors.lib/compressor_mono:author", "Julius O. Smith III");
		m->declare("compressors.lib/compressor_mono:copyright", "Copyright (C) 2014-2020 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("compressors.lib/compressor_mono:license", "MIT-style STK-4.3 license");
		m->declare("compressors.lib/name", "Faust Compressor Effect Library");
		m->declare("compressors.lib/version", "1.6.0");
		m->declare("filename", "fx_deess.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_deess");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/onePoleSwitching:author", "Jonatan Liljedahl, revised by Dario Sanfilippo");
		m->declare("signals.lib/onePoleSwitching:licence", "STK-4.3");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = std::exp(-(1e+03f / fConst0));
		fConst3 = std::exp(-(2e+01f / fConst0));
		fConst4 = std::exp(-(5e+02f / fConst0));
		fConst5 = 1.0f - fConst2;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(5.5e+03f);
		fHslider1 = FAUSTFLOAT(-32.0f);
		fHslider2 = FAUSTFLOAT(4.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec5[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec1[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec8[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec11[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec10[l13] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual FxDeess* clone() {
		return new FxDeess();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_deess");
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(5.5e+03f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(9e+03f), FAUSTFLOAT(1e+01f));
		ui_interface->addHorizontalSlider("ratio", &fHslider2, FAUSTFLOAT(4.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("thresh", &fHslider1, FAUSTFLOAT(-32.0f), FAUSTFLOAT(-6e+01f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = FxDeess_faustpower2_f(fSlow0);
		float fSlow2 = 1.0f / fSlow1;
		float fSlow3 = 2.0f * (1.0f - fSlow2);
		float fSlow4 = 1.0f / fSlow0;
		float fSlow5 = (fSlow4 + -1.0f) / fSlow0 + 1.0f;
		float fSlow6 = (fSlow4 + 1.0f) / fSlow0 + 1.0f;
		float fSlow7 = 1.0f / fSlow6;
		float fSlow8 = 1.0f - fSlow4;
		float fSlow9 = 1.0f / (fSlow4 + 1.0f);
		float fSlow10 = float(fHslider1);
		float fSlow11 = 1.0f / (fSlow1 * fSlow6);
		float fSlow12 = fConst5 * (1.0f / std::max<float>(1.1920929e-07f, float(fHslider2)) + -1.0f);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			fVec0[0] = fTemp0;
			fRec1[0] = -(fSlow9 * (fSlow8 * fRec1[1] - fSlow4 * (fTemp0 - fVec0[1])));
			fRec0[0] = fRec1[0] - fSlow7 * (fSlow5 * fRec0[2] + fSlow3 * fRec0[1]);
			float fTemp1 = 2.0f * fRec0[1];
			float fTemp2 = std::fabs(fSlow11 * (fRec0[2] + (fRec0[0] - fTemp1)));
			float fTemp3 = ((fTemp2 > fRec3[1]) ? fConst4 : fConst3);
			fRec3[0] = fTemp2 * (1.0f - fTemp3) + fRec3[1] * fTemp3;
			fRec2[0] = fSlow12 * std::max<float>(2e+01f * std::log10(std::max<float>(1.1754944e-38f, fRec3[0])) - fSlow10, 0.0f) + fConst2 * fRec2[1];
			fRec5[0] = -(fSlow9 * (fSlow8 * fRec5[1] - (fTemp0 + fVec0[1])));
			fRec4[0] = fRec5[0] - fSlow7 * (fSlow5 * fRec4[2] + fSlow3 * fRec4[1]);
			output0[i0] = FAUSTFLOAT(fSlow7 * (fRec4[2] + fRec4[0] + 2.0f * fRec4[1] + fSlow2 * std::pow(1e+01f, 0.05f * fRec2[0]) * (fRec0[0] + fRec0[2] - fTemp1)));
			float fTemp4 = float(input1[i0]);
			fVec1[0] = fTemp4;
			fRec7[0] = -(fSlow9 * (fSlow8 * fRec7[1] - fSlow4 * (fTemp4 - fVec1[1])));
			fRec6[0] = fRec7[0] - fSlow7 * (fSlow5 * fRec6[2] + fSlow3 * fRec6[1]);
			float fTemp5 = 2.0f * fRec6[1];
			float fTemp6 = std::fabs(fSlow11 * (fRec6[2] + (fRec6[0] - fTemp5)));
			float fTemp7 = ((fTemp6 > fRec9[1]) ? fConst4 : fConst3);
			fRec9[0] = fTemp6 * (1.0f - fTemp7) + fRec9[1] * fTemp7;
			fRec8[0] = fSlow12 * std::max<float>(2e+01f * std::log10(std::max<float>(1.1754944e-38f, fRec9[0])) - fSlow10, 0.0f) + fConst2 * fRec8[1];
			fRec11[0] = -(fSlow9 * (fSlow8 * fRec11[1] - (fTemp4 + fVec1[1])));
			fRec10[0] = fRec11[0] - fSlow7 * (fSlow5 * fRec10[2] + fSlow3 * fRec10[1]);
			output1[i0] = FAUSTFLOAT(fSlow7 * (fRec10[2] + fRec10[0] + 2.0f * fRec10[1] + fSlow2 * std::pow(1e+01f, 0.05f * fRec8[0]) * (fRec6[0] + fRec6[2] - fTemp5)));
			fVec0[1] = fVec0[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec3[1] = fRec3[0];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fVec1[1] = fVec1[0];
			fRec7[1] = fRec7[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec9[1] = fRec9[0];
			fRec8[1] = fRec8[0];
			fRec11[1] = fRec11[0];
			fRec10[2] = fRec10[1];
			fRec10[1] = fRec10[0];
		}
	}

};

#endif
