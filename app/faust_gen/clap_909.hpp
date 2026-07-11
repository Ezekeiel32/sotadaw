/* ------------------------------------------------------------
name: "clap_909"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Clap909 -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Clap909_H__
#define  __Clap909_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Clap909
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

static float Clap909_faustpower2_f(float value) {
	return value * value;
}

class Clap909 : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	FAUSTFLOAT fHslider0;
	float fConst8;
	FAUSTFLOAT fButton0;
	int IOTA0;
	float fVec0[16384];
	FAUSTFLOAT fHslider1;
	float fConst9;
	float fVec1[2];
	int iRec2[2];
	float fConst10;
	float fConst11;
	FAUSTFLOAT fHslider2;
	float fConst12;
	float fVec2[2];
	int iRec3[2];
	float fConst13;
	float fConst14;
	float fVec3[2];
	int iRec4[2];
	int iRec5[2];
	int iRec6[2];
	float fRec1[3];
	float fRec0[3];
	FAUSTFLOAT fHslider3;
	float fConst15;
	
 public:
	Clap909() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Clap909 -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "clap_909.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "clap_909");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(1570.7964f / fConst0);
		float fConst2 = Clap909_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = 3.1415927f / fConst0;
		fConst9 = 0.028f * fConst0;
		fConst10 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst11 = 1.0f / fConst10;
		fConst12 = 0.019f * fConst0;
		fConst13 = 1.0f / std::max<float>(1.0f, 0.03f * fConst0);
		fConst14 = 0.01f * fConst0;
		fConst15 = 1.6f / (fConst2 * fConst6);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(1.4e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(1.0f);
		fHslider2 = FAUSTFLOAT(0.24f);
		fHslider3 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		IOTA0 = 0;
		for (int l0 = 0; l0 < 16384; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fVec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec3[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec3[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec4[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec5[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec6[l8] = 0;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec1[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec0[l10] = 0.0f;
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
	
	virtual Clap909* clone() {
		return new Clap909();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("clap_909");
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(0.24f), FAUSTFLOAT(0.08f), FAUSTFLOAT(0.8f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("spread", &fHslider1, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.3f), FAUSTFLOAT(2.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(1.4e+03f), FAUSTFLOAT(6e+02f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(1e+01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst8 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / Clap909_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -0.8333333f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 0.8333333f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fButton0);
		float fSlow7 = float(fHslider1);
		int iSlow8 = int(fConst9 * fSlow7);
		float fSlow9 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		int iSlow10 = int(fConst12 * fSlow7);
		int iSlow11 = int(fConst14 * fSlow7);
		float fSlow12 = 1.0f / (fSlow0 * fSlow4);
		float fSlow13 = fConst15 * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[IOTA0 & 16383] = fSlow6;
			float fTemp0 = fVec0[(IOTA0 - iSlow8) & 16383];
			fVec1[0] = fTemp0;
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fTemp0 <= fVec1[1]) + (fTemp0 > fVec1[1]);
			float fTemp1 = float(iRec2[0]);
			float fTemp2 = fVec0[(IOTA0 - iSlow10) & 16383];
			fVec2[0] = fTemp2;
			iRec3[0] = (iRec3[1] + (iRec3[1] > 0)) * (fTemp2 <= fVec2[1]) + (fTemp2 > fVec2[1]);
			float fTemp3 = float(iRec3[0]);
			float fTemp4 = fVec0[(IOTA0 - iSlow11) & 16383];
			fVec3[0] = fTemp4;
			iRec4[0] = (iRec4[1] + (iRec4[1] > 0)) * (fTemp4 <= fVec3[1]) + (fTemp4 > fVec3[1]);
			float fTemp5 = float(iRec4[0]);
			float fTemp6 = fVec0[(IOTA0 - 1) & 16383];
			iRec5[0] = (iRec5[1] + (iRec5[1] > 0)) * (fSlow6 <= fTemp6) + (fSlow6 > fTemp6);
			float fTemp7 = float(iRec5[0]);
			iRec6[0] = 1103515245 * iRec6[1] + 12345;
			fRec1[0] = float(iRec6[0]) * (2.3283064e-10f * std::max<float>(0.0f, std::min<float>(fConst11 * fTemp7, fConst13 * (fConst10 - fTemp7) + 1.0f)) + 2.561137e-10f * std::max<float>(0.0f, std::min<float>(fConst11 * fTemp5, fConst13 * (fConst10 - fTemp5) + 1.0f)) + 2.7939678e-10f * std::max<float>(0.0f, std::min<float>(fConst11 * fTemp3, fConst13 * (fConst10 - fTemp3) + 1.0f)) + 4.1909515e-10f * std::max<float>(0.0f, std::min<float>(fConst11 * fTemp1, fSlow9 * (fConst10 - fTemp1) + 1.0f))) - fSlow5 * (fSlow3 * fRec1[2] + fSlow1 * fRec1[1]);
			fRec0[0] = fSlow12 * (fRec1[0] - fRec1[2]) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			float fTemp8 = tanhf(fSlow13 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]));
			output0[i0] = FAUSTFLOAT(fTemp8);
			output1[i0] = FAUSTFLOAT(fTemp8);
			IOTA0 = IOTA0 + 1;
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fVec2[1] = fVec2[0];
			iRec3[1] = iRec3[0];
			fVec3[1] = fVec3[0];
			iRec4[1] = iRec4[0];
			iRec5[1] = iRec5[0];
			iRec6[1] = iRec6[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
